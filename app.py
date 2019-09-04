from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length
import config
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(config)

baseDir = os.path.abspath(os.path.dirname(__file__))
sqlitePath = os.path.join(baseDir, 'user.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + sqlitePath
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

class NameForm(FlaskForm):
    name = StringField('', validators=[DataRequired(), Length(3,30)], render_kw={"placeholder": 'Enter name', "value": ""})
    password = PasswordField('', validators=[DataRequired()], render_kw={"placeholder": 'Enter password', "value": ""})
    submit = SubmitField('Submit')

class ArticleForm(FlaskForm):
    title = StringField('', validators=[DataRequired()], render_kw={"placeholder": 'Enter title', "value": ""})
    subtitle = StringField('', validators=[DataRequired()], render_kw={"placeholder": 'Enter subtitle', "value": ""})
    content = TextAreaField('', validators=[DataRequired()], render_kw={"placeholder": 'Enter content', "value": "", "rows": "10"})
    submit = SubmitField('Submit')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    pwd = db.Column(db.String())

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            nullable=False)
    user = db.relationship('User',
                               backref=db.backref('articles', lazy=True))

db.create_all()

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    username = session.get('username')
    userid = session.get('id')
    if username is not None:
        articles = Article.query.filter_by(user_id=userid)
        return render_template('person.html', name=username, userid=userid, articles=articles)
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user and user.pwd == form.password.data:
            session['username'] = form.name.data
            session['id'] = user.id
            return redirect(url_for('hello_world'))
    return render_template("index.html", form=form)

@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/success/', methods=['GET', 'POST'])
def success():
    return render_template("success.html")

@app.route('/register/', methods=['GET', 'POST'])
def register():
    code = 0
    form = NameForm()
    if form.validate_on_submit():
        old_user = User.query.filter_by(name=form.name.data).first()
        if old_user is None:
            user = User(name=form.name.data, pwd=form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('hello_world'))
        else:
            code = 1
    return render_template('register.html', form=form, code=code)

@app.route('/logout/')
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect(url_for('hello_world'))

@app.route('/edit/', methods=['GET', 'POST'])
def edit():
    form = ArticleForm()
    if form.validate_on_submit():
        user_id = session.get('id')
        if user_id is not None:
            article = Article(title=form.title.data, desc=form.subtitle.data, content=form.content.data, user_id=user_id)
            db.session.add(article)
            db.session.commit()
            articles = Article.query.filter_by(user_id=user_id)
            username = session.get('username')
            return render_template('person.html', name=username, userid=user_id, articles=articles)
    return render_template('edit.html', form=form)

@app.route('/read/<article_id>/')
def read(article_id):
    article = Article.query.filter_by(id=article_id).first()
    return render_template('read.html', article=article)

if __name__ == '__main__':
    app.run()
