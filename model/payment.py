from app import db, ma, datetime


class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False)

    def __init__(self, sender_id, receiver_id, amount, due_date):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.amount = amount
        if isinstance(due_date, datetime.date):
            self.due_date = due_date
        else:
            self.due_date = datetime.date.fromisoformat(due_date)
        self.completed = False


class PaymentSchema(ma.Schema):
    class Meta:
        fields = ("payment_id", "sender_id", "receiver_id", "amount", "due_date", "paid_date")
        model = Payment


payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
