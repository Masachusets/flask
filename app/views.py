from flask.views import MethodView
from typing import Type
from sqlalchemy.exc import IntegrityError
from flask import jsonify, request

from models import Session, UserModel, AdModel
from validate import HttpError, validate


def get_by_id(item_id: int, orm_model: Type[UserModel], session):
    orm_item = session.query(orm_model).get(item_id)
    if orm_item is None:
        raise HttpError(404, 'Item not found')
    return orm_item


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = get_by_id(user_id, UserModel, session)
            return jsonify({
                'username': user.name,
                'email': user.email,
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

    def put(self):
        pass

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
                'creation_time': ad.creation_time.isoformat()
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            try:
                new_ad = AdModel(**validate(json_data, CreateAdSchema))
                session.add(new_ad)
                session.commit()
            except IntegrityError:
                raise HttpError(409, 'name already exist')
            return jsonify({'status': 'Ok', 'ad_id': new_ad.id})

    def put(self):
        pass

    def patch(self, ad_id: int):
        data_to_patch = validate(request.json, PatchAdSchema)
        with Session() as session:
            ad = get_by_id(ad_id, UserModel, session)
            for field, value in data_to_patch.items():
                setattr(ad, field, value)
            session.commit()
            return jsonify({'status': 'ad changed'})

    def delete(self, ad_id: int):
        with Session() as session:
            ad = get_by_id(ad_id, AdModel, session)
            session.delete(ad)
        session.commit()
        return jsonify({'status': 'ad deleted'})