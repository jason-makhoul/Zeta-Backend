from app import db, ma, datetime


class Offer(db.Model):
    offer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(length=255))
    amount = db.Column(db.Float, nullable=False)
    interest = db.Column(db.Float, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    offer_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    is_accepted = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_id, amount, interest, score, due_date, description=''):
        self.user_id = user_id
        self.amount = float(amount)
        self.interest = float(interest)
        self.score = int(score)
        self.offer_date = datetime.date.today()
        self.due_date = due_date
        self.description = description if description else ''
        self.is_accepted = False


class OfferSchema(ma.Schema):
    class Meta:
        fields = ("offer_id", "user_id", "amount", "interest", "score", "description", "offer_date", "due_date", "is_accepted")
        model = Offer


offer_schema = OfferSchema()
offers_schema = OfferSchema(many=True)
