from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from models import db, Event, User
from datetime import datetime, timedelta
import os
from lunarcalendar import Converter, Solar
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join("static", "uploads")
app.secret_key = "supersecret"  # 🔹 必須設定 session 金鑰

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# -------------------------
# 登入 / 註冊 / 登出
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(username=username).first():
            flash("帳號已存在")
            return redirect(url_for("register"))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("註冊成功，請登入")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        flash("登入失敗，帳號或密碼錯誤")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# -------------------------
# 首頁
# -------------------------
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# -------------------------
# 取得事件 (僅當前使用者)
# -------------------------
@app.route("/get_events")
@login_required
def get_events():
    events = Event.query.filter_by(user_id=current_user.id).all()
    event_list = []

    for e in events:
        start_date = datetime.strptime(e.date, "%Y-%m-%d")
        repeat_dates = [start_date]

        if e.repeat_rule == "daily":
            repeat_dates = [start_date + timedelta(days=i) for i in range(0, 90)]
        elif e.repeat_rule == "weekly":
            repeat_dates = [start_date + timedelta(weeks=i) for i in range(0, 12)]
        elif e.repeat_rule == "monthly":
            repeat_dates = [start_date + timedelta(days=30 * i) for i in range(0, 6)]
        elif e.repeat_rule == "every_3_days":
            repeat_dates = [start_date + timedelta(days=3 * i) for i in range(0, 30)]

        for d in repeat_dates:
            event_list.append({
                "id": e.id,
                "title": f"[{e.tag}] {e.title}" if e.tag else e.title,
                "start": f"{d.strftime('%Y-%m-%d')}T{e.time}",
                "end": f"{d.strftime('%Y-%m-%d')}T{e.end_time}" if e.end_time else None,
                "color": e.color,
                "tag": e.tag,
                "repeat_rule": e.repeat_rule,
                "diary": e.diary,
                "image": e.image_path
            })

    return jsonify(event_list)

# -------------------------
# 新增事件 (綁定使用者)
# -------------------------
@app.route("/add_event", methods=["POST"])
@login_required
def add_event():
    title = request.form.get("title", "")
    date = request.form.get("date", "")
    time = request.form.get("time", "00:00")
    end_time = request.form.get("end_time", None)
    tag = request.form.get("tag", "")
    repeat_rule = request.form.get("repeat_rule", "none")
    diary = request.form.get("diary", "")
    color = request.form.get("color", "#007bff")

    image_file = request.files.get("image")
    image_path = None
    if image_file and image_file.filename != "":
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        filename = datetime.now().strftime("%Y%m%d%H%M%S_") + image_file.filename
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(file_path)
        image_path = file_path

    new_event = Event(
        title=title or ("📖 日記" if diary else "🖼️ 圖片"),
        date=date,
        time=time,
        end_time=end_time,
        tag=tag,
        repeat_rule=repeat_rule,
        diary=diary,
        image_path=image_path,
        color=color,
        user_id=current_user.id  # 🔹 關聯使用者
    )
    db.session.add(new_event)
    db.session.commit()
    return redirect(url_for("index"))

# -------------------------
# 日記專區
# -------------------------
@app.route("/diaries")
@login_required
def diaries():
    diaries = Event.query.filter(
        Event.user_id == current_user.id,
        Event.diary.isnot(None),
        Event.diary != ""
    ).order_by(Event.date.desc()).all()
    return render_template("diaries.html", diaries=diaries)

# -------------------------
# 農曆 API
# -------------------------
@app.route("/get_lunar/<date>")
def get_lunar(date):
    try:
        year, month, day = map(int, date.split("-"))
        solar = Solar(year, month, day)
        lunar = Converter.Solar2Lunar(solar)
        lunar_str = f"{lunar.month}月{lunar.day}"
    except Exception:
        lunar_str = ""
    return jsonify({"lunar": lunar_str})


if __name__ == "__main__":
    app.run(debug=True)
