
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drone_city.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


with app.app_context():
    db.create_all()


# Контекст-процессор для проверки авторизации в шапке
@app.context_processor
def inject_user():
    class SimpleUser:
        def __init__(self, user_id):
            self.is_authenticated = bool(user_id)

    return dict(current_user=SimpleUser(session.get('user_id')))


@app.route('/')
def index():
    return render_template('index.html')


# Перенаправляем старые ссылки about на регистрацию
@app.route('/about', methods=['GET', 'POST'])
def about():
    return redirect(url_for('register'))


@app.route('/malvina')
def character_malvina():
    if not session.get('user_id'):
        flash('Пожалуйста, войдите в систему, чтобы просмотреть информацию о персонаже.', 'danger')
        return redirect(url_for('login'))
    return render_template('character_malvina.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/information')
def information():
    return render_template('information.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        surname = request.form.get('surname')
        name = request.form.get('name')
        patronymic = request.form.get('patronymic')
        age = request.form.get('age')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Пользователь с таким email уже существует.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            surname=surname,
            name=name,
            patronymic=patronymic,
            age=age,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)