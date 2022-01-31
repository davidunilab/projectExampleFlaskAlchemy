from faker import Faker
from run import db, UserModel, PostModel
from werkzeug.security import generate_password_hash
from random import random
db.create_all()


fake = Faker()
for i in range(1, 200):
    user = UserModel(username=fake.name(), email=fake.email(), password=generate_password_hash("password"))
    db.session.add(user)
    db.session.commit()


for i in range(1, 200):
    post = PostModel(title=fake.paragraph(nb_sentences=1), body=fake.text(), user_id=abs(i-200))
    db.session.add(post)
    db.session.commit()