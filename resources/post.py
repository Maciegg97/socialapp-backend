import traceback

from flask_restful import Resource
from flask import request

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from models.post import PostModel
from models.user import UserModel
from models.vote import VoteModel
from schemas.post import PostCreateSchema, PostSchema
from libs.strings import gettext

post_create_schema = PostCreateSchema()
post_schema = PostSchema()


class PostCreate(Resource):
    @classmethod
    @jwt_required(fresh=True)
    def post(cls):
        user_id = get_jwt_identity()
        post_json = request.get_json()
        post_json['owner_id'] = user_id

        post_content = post_create_schema.load(post_json)

        try:
            post_content.save_to_db()
            return {"message": gettext("post_created")}, 201
        except:
            traceback.print_exc()
            post_content.delete_from_db()  # rollback
            return {"message": gettext("post_error_creating")}, 500


class AllPost(Resource):
    @classmethod
    def get(cls):
        posts = PostModel.find_all()
        response = post_schema.dump(posts, many=True)
        for r in response:
            r['votes'] = VoteModel.count_post_votes(r['id'])
        return response, 200


class AllUserPosts(Resource):
    @classmethod
    def get(cls, username: str):

        owner = UserModel.find_by_username(username)

        if not owner:
            return {"message": gettext("user_not_found")}, 404

        response = post_schema.dump(PostModel.find_all_by_owner_id(owner.id), many=True)

        for r in response:
            r['votes'] = VoteModel.count_post_votes(r['id'])

        return response, 200


class Post(Resource):
    @classmethod
    def get(cls, post_id: int):

        post = PostModel.find_by_id(post_id)

        if not post:
            return {"message": gettext("post_not_found").format(post_id)}, 404

        votes_number = VoteModel.count_post_votes(post_id)

        response = post_schema.dump(post)
        response['votes'] = votes_number

        return response, 200

    @classmethod
    @jwt_required(fresh=True)
    def put(cls, post_id: int):
        user_id = get_jwt_identity()
        post_json = request.get_json()

        post_data = post_create_schema.load(post_json, partial=("owner_id",))

        post_to_update = PostModel.find_by_id(post_id)

        if post_to_update.owner_id != user_id:
            return {"message": gettext("not_post_owner")}, 403

        post_to_update.content = post_data.content
        post_to_update.title = post_data.title

        try:
            post_to_update.save_to_db()
            return post_create_schema.dump(post_to_update), 201
        except:
            traceback.print_exc()
            post_to_update.delete_from_db()  # rollback
            return {"message": gettext("post_error_update")}, 500

    @classmethod
    @jwt_required(fresh=True)
    def delete(cls, post_id: int):
        user_id = get_jwt_identity()

        post_to_delete = PostModel.find_by_id(post_id)

        if not post_to_delete.owner_id == user_id:
            return {"message": gettext("not_post_owner")}, 403

        try:
            post_to_delete.delete_from_db()
            return {"message": gettext("post_deleted")}
        except:
            traceback.print_exc()
            return {"message": gettext("post_error_deleting")}, 500
