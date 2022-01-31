from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Our-secret-key'


db = SQLAlchemy(app)
jwt = JWTManager(app)

resource_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
}

class Auth(Resource):
    def post(self):
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if username != "test" or password != "test":
            return jsonify({"msg": "Bad username or password"}), 401

        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class PostModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Post %r>' % self.title

# quit()



userParser = reqparse.RequestParser()
userParser.add_argument("username", type=str, help="user name should be string")
userParser.add_argument("email", type=str, help="Email should be string")


class Post(Resource):
    def get(self, post_id):
        pass

    def post(self, post_id):
        pass

    def put(self, post_id):
        pass

    def delete(self, post_id):
        pass


# CRUD
class User(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self, user_id):
        if user_id == 999:
            return UserModel.query.all()
        user = UserModel.query.filter_by(id=user_id).first()
        return user

    @marshal_with(resource_fields)
    def post(self, user_id):
        args = userParser.parse_args()
        user = UserModel(username=args["username"], email=args["email"])
        db.session.add(user)
        db.session.commit()
        return "inserted"

    @marshal_with(resource_fields)
    def put(self, user_id):
        args = userParser.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        if user == None:
            user = UserModel(username=args["username"], email=args["email"])
        else:
            user.username = args["username"]
            user.email = args["email"]

        db.session.add(user)
        db.session.commit()
        return "edited"

    def delete(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()

        return f"deleted user with id {user_id}"


api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Post, '/post/<int:post_id>')
api.add_resource(Auth, '/login')


if __name__ == "__main__":
    app.run(debug=True, port=5000)