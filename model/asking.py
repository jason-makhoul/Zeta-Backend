from app import db, ma, datetime


class Asking(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(length=255))
    amount = db.Column(db.Float, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    repay_date = db.Column(db.Date, nullable=False)
    is_accepted = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_id, amount, repay_date, score=0, description=''):

        self.user_id = user_id
        self.amount = float(amount)
        self.score = int(score)
        self.request_date = datetime.date.today()
        self.repay_date = repay_date
        self.description = description if description else ''
        self.is_accepted = False


class AskingSchema(ma.Schema):
    class Meta:
        fields = ("request_id", "user_id", "amount", "score", "description", "request_date", "repay_date", "is_accepted")
        model = Asking


asking_schema = AskingSchema()
askings_schema = AskingSchema(many=True)
