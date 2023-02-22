import traceback

from pydantic import ValidationError
from flask_restful import Resource
from flask import request

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from models.vote import VoteModel
from models.post import PostModel
from schemas.vote import VoteSchema
from libs.strings import gettext


class Vote(Resource):
    @classmethod
    @jwt_required(fresh=True)
    def post(cls):
        current_user_id = get_jwt_identity()
        vote_json = request.get_json()

        try:
            validated_vote = VoteSchema(**vote_json)
        except ValidationError as e:
            return {"message": gettext("vote_validation_error").format(e)}, 400

        post = PostModel.find_by_id(validated_vote.post_id)
        if not post:
            return {"message": gettext("post_not_found").format(post.id)}, 404

        found_vote = VoteModel.find_vote(current_user_id, post.id)

        if validated_vote.dir == 1:
            if found_vote:
                return {"message": gettext("double_vote").format(current_user_id, post.id)}
            new_vote = VoteModel(user_id=current_user_id, post_id=post.id)
            new_vote.save_to_db()
            return {"message": gettext("vote_added")}, 201
        else:
            if not found_vote:
                return {"message": gettext("post_not_voted")}, 400

            found_vote.delete_from_db()

            return {"message": gettext("vote_deleted")}, 200
