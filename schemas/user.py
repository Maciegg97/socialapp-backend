import re


from ma import ma
from marshmallow import pre_dump, Schema, fields, validates, ValidationError, validate, validates_schema, post_load
from models.user import UserModel
from libs.strings import gettext


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        load_only = ("password",)
        dump_only = ("id", "confirmation", "created_at")


class UserCreationSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone_number = fields.Str(required=False)
    age = fields.Int(required=True, validate=validate.Range(min=1, max=120))

    @validates("password")
    def validates_password(self, value):
        if len(value) < 8:
            raise ValidationError(gettext("password_too_short"))
        if not any(i.isupper() for i in value):
            raise ValidationError(gettext("password_upper_case"))
        if not any(i.islower() for i in value):
            raise ValidationError(gettext("password_lower_case"))

    @validates("email")
    def validates_email(self, value):
        if not re.match("^[a-zA-Z0-9-_().]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]{2,6}$", value):
            raise ValidationError(gettext("invalid_email_format"))

    @validates("phone_number")
    def validates_phone_number(self, value):
        if not re.match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{3,7}$", value):
            raise ValidationError(gettext("invalid_phone_number_format"))

    @pre_dump
    def _pre_dump(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user

    @post_load
    def make_user(self, data, **kwargs):
        return UserModel(**data)


class UserChangePassword(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)
    new_password_2 = fields.Str(required=True)

    @validates("new_password")
    def validates_password(self, value):
        if len(value) < 8:
            raise ValidationError(gettext("password_too_short"))
        if not any(i.isupper() for i in value):
            raise ValidationError(gettext("password_upper_case"))
        if not any(i.islower() for i in value):
            raise ValidationError(gettext("password_lower_case"))






