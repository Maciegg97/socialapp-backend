from ma import ma
from marshmallow import Schema, fields, validate, post_load

from models.post import PostModel


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PostModel
        load_instance = True
        dump_only = ("owner_id", "owner", "created_at", "id")
        include_fk = True


class PostCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(2, 120))
    content = fields.Str(required=True, validate=validate.Length(2, 500))
    owner_id = fields.Int(required=True)

    @post_load
    def make_post(self, data, **kwargs):
        return PostModel(**data)
