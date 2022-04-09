from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import jwt
import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootroot@127.0.0.1:3306/zeta'
CORS(app)
db = SQLAlchemy(app)
SECRET_KEY = "b'|\xe7\xbfU3`\xc4\xec\xa7\xa9zf:}\xb5\xc7\xb9\x139^3@Dv'"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True)
    hashed_password = db.Column(db.String(128))

    def __init__(self, user_name, password):
        super(User, self).__init__(user_name=user_name)
        self.hashed_password = bcrypt.generate_password_hash(password)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_name")
        model = User


user_schema = UserSchema()


def create_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=4),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )


def extract_auth_token(authenticated_request):
    auth_header = authenticated_request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return None


def decode_token(token):
    payload = jwt.decode(token, SECRET_KEY, 'HS256')
    return payload['sub']


@app.route('/user', methods=['POST'])
def user():
    _json = request.json
    user_name = _json['user_name']
    password = _json['password']
    new_user = User(user_name, password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_schema.dump(new_user))


@app.route('/authentication', methods=['POST'])
def authentication():
    _json = request.json
    user_name = _json['user_name']
    password = _json['password']
    if user_name is None or password is None:
        abort(400)
    else:
        userFilter = User.query.filter_by(user_name=user_name).first()
        if userFilter is None:
            abort(403)
        elif bcrypt.check_password_hash(userFilter.hashed_password, password):
            newToken = create_token(userFilter.id)
            return jsonify({"token": newToken})
        else:
            abort(403)
