from app import db, ma, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(length=255), nullable=False, unique=True)
    user_email = db.Column(db.String(length=255), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    wallet = db.Column(db.Float, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    occupation = db.Column(db.String(length=255))
    is_Admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_name, user_email, password, is_Admin, occupation='', wallet=0.0):
        self.user_name = user_name
        self.user_email = user_email
        self.hashed_password = bcrypt.generate_password_hash(password)
        self.wallet = wallet if wallet else 0.0
        self.occupation = occupation if occupation else ''
        self.credit_score = 0
        self.is_Admin = is_Admin if is_Admin else False


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_name", "user_email", "wallet", "occupation", "credit_score", "is_Admin")
        model = User


user_schema = UserSchema()
