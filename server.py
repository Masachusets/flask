from flask import jsonify

from app.views import UserView, AdView
from app.models import app


app.add_url_rule('/user/<int:user_id>', view_func=UserView.as_view('users_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/user/', view_func=UserView.as_view('users'), methods=['POST'])
app.add_url_rule('/ap/<int:ap_id>', view_func=AdView.as_view('ads_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/ap/', view_func=AdView.as_view('ads'), methods=['POST'])

app.run()