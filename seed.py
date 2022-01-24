from faker import Faker
from main import db, UserModel, PostModel
fake = Faker()

db.create_all()

for i in range(1,200):
    user = UserModel(username=fake.name(), email=fake.email())
    print(user)
    db.session.add(user)
    db.session.commit()

for i in range(1, 200):
    post = PostModel(title=fake.paragraph(nb_sentences=1), body=fake.text(), user_id=i)
    db.session.add(post)
    db.session.commit()