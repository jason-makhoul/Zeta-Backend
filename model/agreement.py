from app import db, ma


class Agreement(db.Model):
    agreement_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('asking.request_id'), nullable=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.offer_id'), nullable=True)
    message = db.Column(db.String(length=255), nullable=False)
    is_accepted = db.Column(db.Boolean, nullable=False)

    def __init__(self, sender_id, receiver_id, offer_id, request_id, message):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.offer_id = offer_id
        self.request_id = request_id
        self.message = message
        self.is_accepted = False


class AgreementSchema(ma.Schema):
    class Meta:
        fields = ("agreement_id", "sender_id", "receiver_id", "request_id", "offer_id", "message")
        model = Agreement


agreement_schema = AgreementSchema()
agreements_schema = AgreementSchema(many=True)
