from flask import Flask, jsonify, request

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager



app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config["JWT_SECRET_KEY"] = "our-secret-key"  # Change this!
db = SQLAlchemy(app)
jwt = JWTManager(app)


resource_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String
}
resource_posts = {
    "id": fields.Integer,
    "title": fields.String,
    "body": fields.String,
    "user_id": fields.Integer
}



registerparser = reqparse.RequestParser()
registerparser.add_argument("email", type=str, required=True, help='Email must be string')
registerparser.add_argument("password", type=str, required=True, help='Password must be string')
registerparser.add_argument("username", type=str, help='user_name must be string')


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




userparser = reqparse.RequestParser()
userparser.add_argument("username", type=str, help='user_name must be string')
userparser.add_argument("email", type=str, help='Email must be string')


postparser = reqparse.RequestParser()
postparser.add_argument("id", type=int, help='Id must be integer')
postparser.add_argument("title", type=str, help='Title must be string')
postparser.add_argument("body", type=str, help='Body must be string')
postparser.add_argument("user_id", type=int, help='User_id must be integer')


class Post(Resource):
    @marshal_with(resource_posts)
    def get(self, post_id):
        if post_id == 000:
            return PostModel.query.all()
        args = postparser.parse_args()
        post = PostModel.query.filter_by(id=post_id).first()
        return post

    @marshal_with(resource_posts)
    def post(self, post_id):
        args = postparser.parse_args()
        post = PostModel(title=args["title"], body=args["body"],user_id=args["user_id"])
        db.session.add(post)
        db.session.commit()
        return "Item has been inserted!"

    @marshal_with(resource_posts)
    def put(self, post_id):
        args = postparser.parse_args()
        post = PostModel.query.filter_by(id=post_id).first()
        if post == None:
            post = PostModel(title=args["title"], body=args["body"], user_id=args["user_id"])
        else:
            post.title = args["title"]
            post.body = args["body"]
            post.user_id = args["user_id"]
        db.session.add(post)
        db.session.commit()
        return "updated"

    # @marshal_with(resource_posts)
    def delete(self, post_id):
        post = PostModel.query.filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        return f"Post with id {post_id} has been deleted"

class User(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self, user_id):
        if user_id == 999:
            return UserModel.query.all()
        args = userparser.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        return user

    @marshal_with(resource_fields)
    @jwt_required()
    def post(self, user_id):
        args = userparser.parse_args()
        password = generate_password_hash(args['password'])
        user = UserModel(username=args['password'], email=args["email"])
        db.session.add(user)
        db.session.commit()
        return "inserted"

    @marshal_with(resource_fields)
    def put(self, user_id):
        args = userparser.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        if user == None:
            user = UserModel(username=args["username"], email=args["email"])
        else:
            user.username = args["username"]
            user.email = args["email"]
        db.session.add(user)
        db.session.commit()
        return "updated"

    # @marshal_with(resource_fiels)
    def delete(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return f"User with id {user_id} has been deleted"


class Auth(Resource):
    def post(self):
        email = request.json.get("email", None)
        password = request.json.get("password", None)

        user = UserModel.query.filter_by(email=email).first()
        if user == None:
            return {"msg": "Email was not found"}

        if email == user.email and check_password_hash(user.password, password):
            return jsonify({"msg": "Bad username or password"}), 401

        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token)

class Register(Resource):
    def post(self):
        args = registerparser.parse_args()
        user = UserModel(username=args['username'], email=args['email'], password=generate_password_hash(args['password']))
        db.session.add(user)
        db.session.commit()
        return {"msg":"created"}, 201


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User {self.username}"

class PostModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Post {self.title}"

      


api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Post, '/post/<int:post_id>')
api.add_resource(Auth, '/login')
api.add_resource(Register, '/register')


@app.before_first_request
def before_first_request():
    import seed


if __name__ == "__main__":
    app.run()
