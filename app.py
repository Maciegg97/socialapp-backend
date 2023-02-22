from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from dotenv import load_dotenv

from db import db
from ma import ma
from blocklist import BLOCKLIST
from resources.confirmation import Confirmation
from resources.user import UserRegister, UserLogin, PhoneNumber, TokenRefresh, UserLogout, User, ChangePassword
from resources.post import PostCreate, Post, AllPost, AllUserPosts
from resources.vote import Vote

app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("default_config")
app.config.from_envvar(
    "APPLICATION_SETTINGS"
)

api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLOCKLIST


api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(ChangePassword, "/user/password")
api.add_resource(PhoneNumber, "/user/number")
api.add_resource(TokenRefresh, "/refresh")

api.add_resource(PostCreate, "/post/create")
api.add_resource(Post, "/post/<int:post_id>")
api.add_resource(AllPost, "/posts")
api.add_resource(AllUserPosts, "/posts/<string:username>")

api.add_resource(Vote, "/vote")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000)