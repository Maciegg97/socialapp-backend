from db import db


class VoteModel(db.Model):
    __tablename__ = "votes"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='cascade'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete='cascade'), primary_key=True)

    def __init__(self, user_id: int, post_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.post_id = post_id

    @classmethod
    def find_vote(cls, user_id: int, post_id: int) -> "VoteModel":
        return cls.query.filter_by(user_id=user_id, post_id=post_id).first()

    @classmethod
    def count_post_votes(cls, _id: int) -> int:
        return cls.query.filter_by(post_id=_id).count()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
