import os
import uuid

from flask import (Flask, abort, flash, jsonify, make_response, redirect,
                   render_template, request, send_from_directory, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.utils import secure_filename

from data import db_session
from data.posts import Post
from data.users import User
from forms import LoginForm, PostForm, RegisterForm

UPLOADS = os.path.join("static", "uploads")
ALLOWED = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key_for_diary_app"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
os.makedirs(UPLOADS, exist_ok=True)
os.makedirs("db", exist_ok=True)

login_mgr = LoginManager()
login_mgr.init_app(app)
login_mgr.login_view = "login"


@login_mgr.user_loader
def load_user(uid):
    return db_session.create_session().get(User, int(uid))


def save_image(fs):
    if not fs or not fs.filename:
        return None
    name = secure_filename(fs.filename)
    if "." not in name or name.rsplit(".", 1)[1].lower() not in ALLOWED:
        return None
    new_name = f"{uuid.uuid4().hex}_{name}"
    fs.save(os.path.join(UPLOADS, new_name))
    return new_name


@app.route("/")
def index():
    sess = db_session.create_session()
    posts = sess.query(Post).order_by(Post.created.desc()).all()
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        if sess.query(User).filter(User.email == form.email.data).first():
            flash("Пользователь с такой почтой уже есть", "danger")
            return render_template("register.html", form=form)
        user = User(name=form.name.data, email=form.email.data)
        user.set_pwd(form.pwd.data)
        sess.add(user)
        sess.commit()
        flash("Регистрация успешна, войдите", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        user = sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_pwd(form.pwd.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("index"))
        flash("Неверная почта или пароль", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        post = Post(title=form.title.data,
                    text=form.text.data,
                    image=save_image(form.image.data),
                    user_id=current_user.id)
        sess.add(post)
        sess.commit()
        flash("Запись добавлена", "success")
        return redirect(url_for("index"))
    return render_template("post_form.html", form=form, title="Новая запись")


@app.route("/post/<int:pid>")
def view_post(pid):
    post = db_session.create_session().get(Post, pid)
    if not post:
        abort(404)
    return render_template("post.html", post=post)


@app.route("/delete/<int:pid>", methods=["POST"])
@login_required
def delete_post(pid):
    sess = db_session.create_session()
    post = sess.get(Post, pid)
    if not post:
        abort(404)
    if post.user_id != current_user.id:
        abort(403)
    if post.image:
        path = os.path.join(UPLOADS, post.image)
        if os.path.exists(path):
            os.remove(path)
    sess.delete(post)
    sess.commit()
    flash("Запись удалена", "info")
    return redirect(url_for("index"))


@app.route("/uploads/<name>")
def uploaded(name):
    return send_from_directory(UPLOADS, name)


@app.route("/api/posts")
def api_posts():
    sess = db_session.create_session()
    posts = sess.query(Post).order_by(Post.created.desc()).all()
    fields = ("id", "title", "text", "image", "created", "author.name")
    return jsonify({"posts": [p.to_dict(only=fields) for p in posts]})


@app.route("/api/posts/<int:pid>")
def api_post(pid):
    post = db_session.create_session().get(Post, pid)
    if not post:
        return make_response(jsonify({"error": "Not found"}), 404)
    fields = ("id", "title", "text", "image", "created", "author.name")
    return jsonify({"post": post.to_dict(only=fields)})


@app.errorhandler(404)
def not_found(_):
    return make_response(render_template("404.html"), 404)


@app.errorhandler(413)
def too_big(_):
    flash("Файл слишком большой (макс. 5 МБ)", "danger")
    return redirect(url_for("add_post"))


if __name__ == "__main__":
    db_session.global_init("db/diary.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
