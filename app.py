import json

from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import jwt
import datetime
from dateutil.relativedelta import relativedelta
from db_config import DB_CONFIG, SECRET_KEY

app = Flask(__name__)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
CORS(app)
db = SQLAlchemy(app)

from model.user import User, user_schema
from model.asking import Asking, askings_schema, asking_schema
from model.offer import Offer, offers_schema, offer_schema
from model.agreement import Agreement, agreement_schema, agreements_schema
from model.payment import Payment, payments_schema, payment_schema
from model.feedback import Feedback


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


def create_payments(amount, interest, date1, date2):
    number_of_months = (date2.year - date1.year) * 12 + date2.month - date1.month
    monthly_payment = amount / number_of_months

    payments = []
    for i in range(number_of_months):
        payments.append({
            'amount': monthly_payment * (1 + interest),
            'due_date': date1 + relativedelta(months=i + 1)
            })

    return payments


@app.route('/user', methods=['POST', 'GET'])
def user():
    if request.method == 'POST':
        _json = request.json
        user_name = _json['user_name']
        password = _json['password']
        email = _json['user_email']
        occupation = _json['occupation']
        is_Admin = _json['is_Admin']
        new_user = User(user_name, email, password, is_Admin, occupation)

        db.session.add(new_user)
        db.session.commit()

        return jsonify(user_schema.dump(new_user))
    elif request.method == 'GET':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                user_id = decode_token(isToken)
                userFilter = User.query.filter_by(id=user_id).first()
                return jsonify(user_schema.dump(userFilter))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)


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


@app.route('/addFunds', methods=['POST'])
def addFunds():
    isToken = extract_auth_token(request)
    if isToken:
        try:
            user_id = decode_token(isToken)
            _json = request.json
            amount = _json['amount']
            userFilter = User.query.filter_by(id=user_id).first()
            userFilter.wallet = userFilter.wallet + amount
            db.session.commit()
            return jsonify(user_schema.dump(userFilter))
        except jwt.ExpiredSignatureError:
            abort(403)
        except jwt.InvalidTokenError:
            abort(403)
    else:
        abort(403)


@app.route('/getUserOffers', methods=['GET'])
def getUserOffers():
    isToken = extract_auth_token(request)
    if isToken:
        try:
            user_id = decode_token(isToken)
            offerFilter = Offer.query.filter_by(user_id=user_id).all()
            return jsonify(offers_schema.dump(offerFilter))
        except jwt.ExpiredSignatureError:
            abort(403)
        except jwt.InvalidTokenError:
            abort(403)
    else:
        abort(403)


@app.route('/getUserAskings', methods=['GET'])
def getUserAskings():
    isToken = extract_auth_token(request)
    if isToken:
        try:
            user_id = decode_token(isToken)
            requestFilter = Asking.query.filter_by(user_id=user_id).all()
            return jsonify(askings_schema.dump(requestFilter))
        except jwt.ExpiredSignatureError:
            abort(403)
        except jwt.InvalidTokenError:
            abort(403)
    else:
        abort(403)


@app.route('/getUserPayments', methods=['GET'])
def getUserPayments():
    isToken = extract_auth_token(request)
    if isToken:
        try:
            user_id = decode_token(isToken)
            paymentFilter = Payment.query.filter_by(sender_id=user_id).all()
            return jsonify(payments_schema.dump(paymentFilter))
        except jwt.ExpiredSignatureError:
            abort(403)
        except jwt.InvalidTokenError:
            abort(403)
    else:
        abort(403)


@app.route('/getUserAgreements', methods=['GET'])
def getUserAgreements():
    isToken = extract_auth_token(request)
    if isToken:
        try:
            user_id = decode_token(isToken)
            agreementFilter = Agreement.query.filter_by(sender_id=user_id).all()
            result = []
            for row in agreementFilter:
                new_id = row.receiver_id
                new_type = "Request" if row.request_id is not None else "Offer"
                username = User.query.filter_by(id=new_id).first().user_name
                email = User.query.filter_by(id=new_id).first().user_email
                data_set = {"agreement_id": row.agreement_id,
                            "receiver_name": username,
                            "receiver_email": email,
                            "type": new_type,
                            "message": row.message}
                result.append(data_set)
            return json.dumps(result)
        except jwt.ExpiredSignatureError:
            abort(403)
        except jwt.InvalidTokenError:
            abort(403)
    else:
        abort(403)


@app.route('/offer', methods=['POST'])
def offer():
    isToken = extract_auth_token(request)

    if isToken:
        try:
            _json = request.json
            amount = _json['amount']
            interest = _json['interest']
            description = _json['description']
            due_date = _json['due_date']
            user_id = decode_token(isToken)
            userFilter = User.query.filter_by(id=user_id).first()
            new_offer = Offer(user_id, amount, interest, userFilter.credit_score, due_date, description)
            db.session.add(new_offer)
            db.session.commit()
            return jsonify(offer_schema.dump(new_offer))
        except jwt.ExpiredSignatureError:
            abort(403)
        except jwt.InvalidTokenError:
            abort(403)
    else:
        abort(403)


@app.route('/asking', methods=['POST'])
def asking():
    isToken = extract_auth_token(request)

    if isToken:
        try:
            _json = request.json
            amount = _json['amount']
            description = _json['description']
            repay_date = _json['repay_date']
            user_id = decode_token(isToken)
            userFilter = User.query.filter_by(id=user_id).first()
            new_asking = Asking(user_id, amount, repay_date, userFilter.credit_score, description)
            db.session.add(new_asking)
            db.session.commit()
            return jsonify(asking_schema.dump(new_asking))
        except jwt.ExpiredSignatureError:
            abort(403)
        except jwt.InvalidTokenError:
            abort(403)
    else:
        abort(403)


@app.route('/publicOffers', methods=['GET', 'POST'])
def publicOffers():
    if request.method == 'GET':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                user_id = decode_token(isToken)
                offerFilter = Offer.query.filter(Offer.user_id != user_id, Offer.is_accepted == False).all()
                return jsonify(offers_schema.dump(offerFilter))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)
    elif request.method == 'POST':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                _json = request.json
                message = _json['message']
                offer_id = _json['offer_id']
                user_id = decode_token(isToken)
                offerFilter = Offer.query.filter_by(offer_id=offer_id).first()
                receiver_id = offerFilter.user_id
                new_agreement = Agreement(user_id, receiver_id, offer_id, None, message)
                offerFilter.is_accepted = True
                db.session.add(new_agreement)
                db.session.commit()
                return jsonify(agreement_schema.dump(new_agreement))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)


@app.route('/publicAskings', methods=['GET', 'POST'])
def publicAskings():
    if request.method == 'GET':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                user_id = decode_token(isToken)
                askingFilter = Asking.query.filter(Asking.user_id != user_id, Asking.is_accepted == False).all()
                return jsonify(askings_schema.dump(askingFilter))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)
    elif request.method == 'POST':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                _json = request.json
                message = _json['message']
                request_id = _json['request_id']
                user_id = decode_token(isToken)
                askingFilter = Asking.query.filter_by(request_id=request_id).first()
                receiver_id = askingFilter.user_id
                new_agreement = Agreement(user_id, receiver_id, None, request_id, message)
                askingFilter.is_accepted = True
                db.session.add(new_agreement)
                db.session.commit()
                return jsonify(agreement_schema.dump(new_agreement))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)


# @app.route('/payment', methods=['POST'])
# def payment():
#     _json = request.json
#     amount = _json['amount']
#     receiver_id = _json['receiver_id']
#     isToken = extract_auth_token(request)
#
#     if isToken:
#         try:
#             user_id = decode_token(isToken)
#             userFilter = User.query.filter_by(id=user_id).first()
#             new_payment = Payment(user_id, receiver_id, amount)
#             db.session.add(new_payment)
#             db.session.commit()
#             return jsonify(payment_schema.dump(new_payment))
#         except jwt.ExpiredSignatureError:
#             abort(403)
#         except jwt.InvalidTokenError:
#             abort(403)
#     else:
#         abort(403)
