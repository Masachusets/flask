import pydantic
from typing import Optional, Type
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask.views import MethodView

from validation import HttpError, validate
from models import UserModel, AdModel, Token, Base


app = Flask('appli')  # create appli
DSN = 'postgresql://appli:1111@127.0.0.1:5433/flask_db'
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
bcrypt = Bcrypt(app)
Base.metadata.create_all(engine)  # makemigrations
auth = HTTPBasicAuth()


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({'status': 'error',
                        'message': error.message})
    response.status_code = error.status_code
    return response


def get_by_id(item_id: int, orm_model: Type[UserModel], session):
    orm_item = session.query(orm_model).get(item_id)
    if orm_item is None:
        raise HttpError(404, 'Item not found')
    return orm_item


@auth.verify_password
def verify_password(username, password):
    with Session() as session:
        user = session.query(UserModel).filter(UserModel.name == username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return username


def check_token(session):
    token = (
        session.query(Token)
        .join(UserModel)
        .filter(
            # UserModel.name == request.headers.get("name"),
            Token.id == request.headers.get("token"),
        )
        .first()
    )
    if token is None:
        raise HttpError(401, "invalid token")
    return token


class CreateUserSchema(pydantic.BaseModel):
    name: str
    password: str

    @pydantic.validator('name')
    def check_name(cls, value: str):
        if len(value) > 32:
            raise ValueError('Name must be less then 32 chars')

        return value

    @pydantic.validator('password')
    def check_password(cls, value: str):
        value = value.encode()
        value = bcrypt.generate_password_hash(value)
        value = value.decode()
        return value


class PatchUserSchema(pydantic.BaseModel):
    name: Optional[str]
    password: Optional[str]

    @pydantic.validator('name')
    def check_name(cls, value: str):
        if len(value) > 32:
            raise ValueError('Name must be less then 32 chars')

        return value

    @pydantic.validator('password')
    def check_password(cls, value: str):
        value = bcrypt.generate_password_hash(value.encode())
        value = value.decode()
        return value


class CreateAdSchema(pydantic.BaseModel):
    title: str
    text: str
    user_id: int

    @pydantic.validator('title')
    def check_title(cls, value: str):
        if len(value) > 32:
            raise ValueError('Name must be less then 32 chars')
        return value


class PatchAdSchema(pydantic.BaseModel):
    title: Optional[str]
    text: Optional[str]
    user_id: Optional[int]

    @pydantic.validator('title')
    def check_title(cls, value: str):
        if len(value) > 32:
            raise ValueError('Name must be less then 32 chars')
        return value


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = get_by_id(user_id, UserModel, session)
            return jsonify({
                'username': user.name,
                'ads': [ad.id for ad in user.ads],
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            try:
                new_user = UserModel(**validate(json_data, CreateUserSchema))
                session.add(new_user)
                session.commit()
            except IntegrityError:
                raise HttpError(409, 'name already exist')
            return jsonify({'status': 'Ok', 'id': new_user.id})

    def patch(self, user_id: int):
        data_to_patch = validate(request.json, PatchUserSchema)
        with Session() as session:
            user = get_by_id(user_id, UserModel, session)
            for field, value in data_to_patch.items():
                setattr(user, field, value)
            session.commit()
            return jsonify({'status': 'user changed'})

    def delete(self, user_id: int):
        with Session() as session:
            user = get_by_id(user_id, UserModel, session)
            session.delete(user)
        session.commit()
        return jsonify({'status': 'user deleted'})


class AdView(MethodView):

    def get(self, ad_id: int):
        with Session() as session:
            ad = get_by_id(ad_id, AdModel, session)
            return jsonify({
                'ad_title': ad.title,
                'creation_time': ad.creation_time.isoformat(),
                'user_id': ad.user_id
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            try:
                json_data['owner'] = check_token(session).user
                json_data['user_id'] = check_token(session).user_id
                new_ad = AdModel(**validate(json_data, CreateAdSchema))
                session.add(new_ad)
                session.commit()
            except IntegrityError:
                raise HttpError(409, 'name already exist')
            return jsonify({'status': 'Ok', 'ad_id': new_ad.id})

    def patch(self, ad_id: int):
        data_to_patch = validate(request.json, PatchAdSchema)
        with Session() as session:
            ad = get_by_id(ad_id, AdModel, session)
            if check_token(session).user_id != ad.user_id:
                raise HttpError(401, "invalid token")
            for field, value in data_to_patch.items():
                setattr(ad, field, value)
            session.commit()
            return jsonify({'status': f'ad with id {ad_id} changed'})

    def delete(self, ad_id: int):
        with Session() as session:
            ad = get_by_id(ad_id, AdModel, session)
            if check_token(session).user_id != ad.user_id:
                raise HttpError(401, "invalid token")
            title = ad.title
            session.delete(ad)
            session.commit()
        return jsonify({'status': f'ad with id {ad_id} deleted'})


Base.metadata.create_all(engine)

app.add_url_rule('/user/<int:user_id>', view_func=UserView.as_view('users_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/user/', view_func=UserView.as_view('users'), methods=['POST'])
app.add_url_rule('/ad/<int:ad_id>', view_func=AdView.as_view('ads_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/ad/', view_func=AdView.as_view('ads'), methods=['POST'])


@app.route('/login/', methods=['POST'])
def login():
    login_data = request.json
    with Session() as session:
        user = (
            session.query(UserModel).filter(
                UserModel.name == login_data['name']
            ).first()
        )
        check_pass = bcrypt.check_password_hash(user.password.encode(),
                                                login_data['password'].encode())
        if user is None or not check_pass:
            raise HttpError(401, "incorrect user or password")
        token = Token(user_id=user.id)
        session.add(token)
        session.commit()
        return jsonify({'token': token.id})


@app.route('/token/<int:user_id>', methods=['POST'])
def get_user_token(user_id):
    with Session() as session:
        token = (
            session.query(Token).filter(
                Token.user_id == user_id
            ).order_by(Token.creation_time.desc()).first()
        )
        return jsonify(token.id)


app.run()
