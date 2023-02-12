import traceback

from flask_restful import Resource
from flask import request
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_refresh_token,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)

from models.user import UserModel
from models.confirmation import ConfirmationModel
from schemas.user import UserCreationSchema, UserSchema
from blocklist import BLOCKLIST
from libs.mailgun import MailGunException
from libs.strings import gettext

user_schema = UserCreationSchema()
user_login_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        new_user = user_schema.load(user_json)

        if UserModel.find_by_username(new_user.username):
            return {"message": gettext("user_username_exists")}, 400

        if UserModel.find_by_email(new_user.email):
            return {"message": gettext("user_email_exists")}, 400

        new_user.password = generate_password_hash(new_user.password)

        try:
            new_user.save_to_db()

            confirmation = ConfirmationModel(new_user.id)
            confirmation.save_to_db()

            new_user.send_confirmation_email()
            return {"message": gettext("user_registered")}, 201
        except MailGunException as e:
            new_user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            new_user.delete_from_db()  # rollback
            return {"message": gettext("user_error_creating")}, 500


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_login_schema.load(user_json,
                                           partial=("email", "first_name", "last_name", "phone_number", "age"))

        user = UserModel.find_by_username(user_data.username)

        if user and check_password_hash(user.password, user_data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {"message": gettext("user_not_confirmed").format(user.email)}, 400
        return {"message": gettext("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()['jti']
        user_id = get_jwt_identity()
        BLOCKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, 200


class PhoneNumber(Resource):
    @classmethod
    @jwt_required(fresh=True)
    def post(cls):
        phone_data = request.get_json()
        new_phone_number = phone_data['phone_number']
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        if user and not user.phone_number:
            user.phone_number = new_phone_number
            user.save_to_db()
            return {"message": gettext("phone_number_added")}, 201

        if user:
            user.phone_number = new_phone_number
            user.save_to_db()
            return {"message": gettext("phone_number_changed")}, 201

        return {"message": gettext("phone_number_error")}, 500


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
