from app import db


class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(length=255), nullable=False)
    is_closed = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content
        self.is_closed = False
