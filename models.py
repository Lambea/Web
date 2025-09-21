from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# 使用者模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# 事件模型
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    end_time = db.Column(db.String(10), nullable=True)
    tag = db.Column(db.String(50), nullable=True)
    repeat_rule = db.Column(db.String(50), default="none")
    diary = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(20), default="#007bff")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # 🔹 關聯使用者
