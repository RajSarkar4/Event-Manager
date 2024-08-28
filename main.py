from datetime import date
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from form import UserRegistration, UserLoginForm, PostCreationForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get('CSRF_KEY')
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', "postgresql://default:dcB9abvgVP4R@ep-steep-bush-a49tm2cc.us-east-1.aws.neon.tech:5432/verceldb")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def user_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated:
            return abort(403)

        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column((String(100)))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("Post", back_populates="author")


class Post(db.Model):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    date: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[str] = mapped_column(String(50), nullable=False)
    end_date: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(String(2000), nullable=False)
    contact: Mapped[str] = mapped_column(String(250), nullable=True)
    form_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    result = db.session.execute(db.select(Post))
    all_posts = result.scalars().all()
    return render_template('index.html', all_posts=all_posts, current_user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = UserRegistration()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == request.form.get('email'))).scalar()
        if result:
            flash('This email is already registered with another account, login instead!')
            return redirect(url_for('login'))
        new_user = User(
            email=request.form.get('email'),
            password=request.form.get('password'),
            name=request.form.get('name')
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Invalid Password, try again!")
                return redirect(url_for('login'))
        else:
            flash('Invalid Email, please try again!')
            return redirect(url_for('login'))

    return render_template('login.html', form=form, current_user=current_user)


@app.route('/make-post', methods=['POST', 'GET'])
@user_only
def make_post():
    form = PostCreationForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            author=current_user,
            subtitle=form.subtitle.data,
            date=date.today().strftime("%B %d, %Y"),
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            details=form.details.data,
            form_url=form.join_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('make-post.html', form=form, current_user=current_user)


@app.route('/profile/<username>')
def view_profile(username):
    if current_user.is_authenticated:
        result = db.session.execute(db.select(Post).where(Post.author_id == current_user.id)).scalars().all()
        return render_template('profile.html', all_posts=result)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>')
def view_post(post_id):
    result = db.session.execute(db.select(Post).where(Post.id == post_id)).scalar()
    return render_template('post.html', post=result, current_user=current_user)


@app.route("/delete/<int:post_id>")
@user_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(Post, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


if __name__ == '__main__':
    app.run(debug=False, port=8000)
