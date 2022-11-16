from flask_httpauth import HTTPBasicAuth
from models import Session, UserModel, AdModel, app


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    with Session() as session:
        name = session.query(orm_model).get(item_id)
        if username in users and \
                check_password_hash(users.get(username), password):
            return username


@app.route('/ap/')
@auth.login_required
def get_resource():
    return jsonify({'data': f'Hello, {g.user.username}!'})