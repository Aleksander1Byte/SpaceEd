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
import data.forms.AnswerTaskForm as ataf
import data.forms.StatsForm as staf
from werkzeug.utils import redirect

from data.forms.LoginForm import LoginForm
from data.forms.RegisterForm import RegisterForm
from data.tasks import Task
from data.theories import Theory
from data.points import Points
from data.users import User
from data.userstats import UserStats

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120  # 5 GB
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/database.db')
DEBUG = True


def get_tasks_and_ratings(db_sess):
    user_group = current_user.group_id
    tasks = (
        db_sess.query(Task)
        .filter(Task.allowed_groups.like(f'%;{user_group};%'))
        .order_by(Task.id)
        .all()
    )
    ratings = list()
    for t in tasks:
        ratings.append(
            (
                db_sess.query(Points)
                .filter((Points.user_id == current_user.id) & (Points.task_id == t.id))
                .first()
            )
        )
    return ratings, tasks


@app.route('/')
def main():
    context = {}
    if current_user.is_authenticated:
        db_sess = create_session()
        ratings, tasks = get_tasks_and_ratings(db_sess)
        didnt = 0
        for i in range(len(tasks)):
            if not ratings[i]:
                didnt += 1
        context.update({'didnt': didnt})
    return render_template(
        'homepage.html',
        title='SpaceEd',
        current_user=current_user,
        **context
    )


@app.route('/theory/<int:id>', methods=['GET', 'POST'])
def view_theory(id):
    db_sess = create_session()
    thr = db_sess.query(Theory).get(id)
    if not (
        str(current_user.group_id) in thr.allowed_groups.split(';')
        or current_user.is_admin
    ):
        abort(403)
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


def get_unique_groups(db_sess):
    users = db_sess.query(User).all()
    unique_groups = dict()
    for user in users:
        gid = user.group_id
        if gid in unique_groups:
            unique_groups[gid].append(user.first_name + ' ' + user.last_name)
        else:
            unique_groups[gid] = [user.first_name + ' ' + user.last_name]
    return unique_groups


@app.route('/tasks', methods=['GET'])
@login_required
def view_tasks():
    db_sess = create_session()
    ratings, tasks = get_tasks_and_ratings(db_sess)
    context = {'tasks': tasks, 'ratings': ratings}
    return render_template('tasks.html', current_user=current_user, **context)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db_sess = create_session()
    stats = (
        db_sess.query(UserStats).filter((UserStats.user_id == current_user.id)).first()
    )
    form = staf.StatsForm(
        weight=stats.weight, height=stats.height, birthday=stats.birthday
    )
    if form.validate_on_submit():
        db_sess.delete(stats)
        stats = UserStats(
            user_id=current_user.id,
            weight=form.weight.data,
            height=form.height.data,
            birthday=form.birthday.data,
        )
        db_sess.add(stats)
        db_sess.commit()
    ratings, tasks = get_tasks_and_ratings(db_sess)
    correct = incorrect = didnt = 0
    for i in range(len(tasks)):
        if ratings[i]:
            if tasks[i].given_points == ratings[i].amount:
                correct += tasks[i].given_points
            else:
                incorrect += tasks[i].given_points
        else:  # Не приступали
            didnt += tasks[i].given_points
    context = {
        'data': [correct, incorrect, didnt],
        'tasks': tasks,
        'ratings': ratings,
        'form': form,
    }
    return render_template('profile.html', current_user=current_user, **context)


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
@admin_only
def new_task():
    form = ctaf.NewTaskForm()
    db_sess = create_session()
    unique_groups = get_unique_groups(db_sess)
    if form.validate_on_submit():
        picture = request.files['picture'] if 'picture' in request.files else None
        task = Task(
            question=form.question.data,
            answer=form.answer.data,
            given_points=int(form.points.data),
            allowed_groups=';',
        )
        allowed_groups = request.form.getlist('group')
        task.set_allowed_groups(allowed_groups)

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
        unique_groups=unique_groups,
    )


@app.route('/task/<int:id>', methods=['GET', 'POST'])
def solve_task(id):
    form = ataf.AnswerTaskForm()
    db_sess = create_session()
    task = db_sess.query(Task).get(id)
    if task is None:
        abort(404)
        return
    if not (
        str(current_user.group_id) in task.allowed_groups.split(';')
        or current_user.is_admin
    ):
        abort(403)
    answered = (
        db_sess.query(Points)
        .filter((Points.user_id == current_user.id) & (Points.task_id == task.id))
        .first()
    )
    if answered:
        return f'За это заданиие у вас {answered.amount} очков'
    if form.validate_on_submit():
        answer = form.answer.data
        if task.answer:
            if task.answer.lower().capitalize() == answer.lower().capitalize():
                point = Points(
                    user_id=current_user.id, task_id=task.id, amount=task.given_points
                )
            else:
                point = Points(user_id=current_user.id, task_id=task.id, amount=0)
            db_sess.add(point)
            db_sess.commit()
            return redirect('/tasks')
        else:
            print('send_to_check')
    context = {'task': task, 'form': form}
    return render_template('solve_task.html', current_user=current_user, **context)


@app.route('/add_theory', methods=['GET', 'POST'])
@login_required
@admin_only
def new_theory():
    form = cthf.NewTheoryForm()
    db_sess = create_session()

    unique_groups = get_unique_groups(db_sess)

    if form.validate_on_submit():
        video = request.files['video'] if 'video' in request.files else None
        picture = request.files['picture'] if 'picture' in request.files else None
        thr = Theory(
            title=form.title.data,
            description=form.description.data.capitalize(),
            allowed_groups=';',
        )
        allowed_groups = request.form.getlist('group')
        thr.set_allowed_groups(allowed_groups)
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
        unique_groups=unique_groups,
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
            group_id=form.group_id.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        stats = UserStats(user_id=user.id)
        db_sess.add(stats)
        db_sess.commit()
        return redirect('/')
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
