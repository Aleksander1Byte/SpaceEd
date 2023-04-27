from functools import wraps

from data.db_session import global_init, create_session
import os
from flask import Flask, render_template, redirect, request
from flask_login import (
    current_user,
    login_user,
    LoginManager,
    login_required,
    logout_user,
)
from werkzeug.exceptions import abort
import data.forms.CreateTheoryForm as cthf
import data.forms.CreateTaskForm as ctaf
from werkzeug.utils import redirect

from data.forms.LoginForm import LoginForm
from data.forms.RegisterForm import RegisterForm
from data.tasks import Task
from data.theories import Theory
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120  # 5 GB
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/database.db')
DEBUG = True


@app.route('/')
def main():
    return render_template(
        'homepage.html',
        title='SpaceEd',
        current_user=current_user,
    )


@app.route('/theory/<int:id>', methods=['GET', 'POST'])
def view_theory(id):
    db_sess = create_session()
    thr = db_sess.query(Theory).get(id)
    if thr is None:
        abort(404)
        return
    context = {'thr': thr}
    return render_template('view_theory.html', current_user=current_user, **context)


def admin_only(func):
    @wraps(func)
    def check(*args, **kwargs):
        if current_user is None:
            abort(405)
        if not current_user.is_admin:
            abort(405)
        return func(*args, **kwargs)

    return check


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
@admin_only
def new_test():
    form = ctaf.NewTaskForm()
    if form.validate_on_submit():
        picture = request.files['picture'] if 'picture' in request.files else None
        db_sess = create_session()
        task = Task(
            question=form.question.data,
        )

        task.set_picture_path(picture)

        db_sess.add(task)
        db_sess.commit()
        return redirect('/')
    return render_template(
        'new_task.html',
        title='Загрузка нового задания',
        current_user=current_user,
        form=form,
        task=None,
    )


@app.route('/add_theory', methods=['GET', 'POST'])
@login_required
@admin_only
def new_theory():
    form = cthf.NewTheoryForm()
    if form.validate_on_submit():
        video = request.files['video'] if 'video' in request.files else None
        picture = request.files['picture'] if 'picture' in request.files else None
        db_sess = create_session()
        thr = Theory(
            title=form.title.data,
            description=form.description.data.capitalize(),
        )

        thr.set_paths(video, picture)

        db_sess.add(thr)
        db_sess.commit()
        return redirect('/')
    return render_template(
        'new_theory.html',
        title='Загрузка теоритического материала',
        current_user=current_user,
        form=form,
        thr=None,
    )


@app.route('/swap')
@login_required
def get_admin():
    db_sess = create_session()
    user = db_sess.query(User).get(current_user.id)
    if user.is_admin:
        user.is_admin = False
    else:
        user.is_admin = True
    db_sess.commit()
    return f'Удивительно! Ваши права перевернулись на {user.is_admin}'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Пароли не совпадают",
                current_user=current_user,
            )
        db_sess = create_session()
        if db_sess.query(User).filter((User.email == form.email.data)).first():
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Такой пользователь уже есть",
                current_user=current_user,
            )
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template(
        'register.html', title='Регистрация', form=form, current_user=current_user
    )


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            'login.html',
            message="Неправильный логин или пароль",
            form=form,
            current_user=current_user,
        )
    return render_template(
        'login.html', title='Авторизация', form=form, current_user=current_user
    )


if __name__ == '__main__':
    if DEBUG:
        PORT = 5050
        HOST = '127.0.0.1'
    else:
        PORT = int(os.environ.get("PORT", 5000))
        HOST = '0.0.0.0'
    ADDRESS = HOST + ':' + str(PORT)
    app.run(host=HOST, port=PORT)
