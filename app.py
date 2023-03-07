from flask import Flask, jsonify, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import InputRequired
from uuid import uuid1
from sqlalchemy import desc
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = "secret_key"

db = SQLAlchemy(app)
Migrate(app, db)
CKEditor(app)

class Statistics(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    temp = db.Column(db.String())
    humid = db.Column(db.String())
    dirt_humid = db.Column(db.String())
    time = db.Column(db.DateTime())

class Menu(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    uuid = db.Column(db.String())
    title = db.Column(db.String())
    content = db.Column(db.Text())
    date = db.Column(db.DateTime())

class UploadMenu(FlaskForm):
    title = StringField(validators=[InputRequired()], render_kw={"placeholder": "Title"})
    content = CKEditorField()
    thumbnail = FileField()
    submit = SubmitField()

@app.route('/', methods=['GET'])
def mainpage():
    return render_template('index.html')

@app.route('/info', methods=['GET', 'POST'])
def infopage():
    if request.method == 'POST':
        stat = Statistics()
        stat.temp = request.args.get('temp')
        stat.humid = request.args.get('humid')
        stat.dirt_humid = request.args.get('dirt_humid')
        stat.time = datetime.today()
        try:
            db.session.add(stat)
            db.session.commit()
            return jsonify({
                "status": "Updated"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "failed",
                "message": str(e)
            })

@app.route('/getCurrentStat', methods=['GET'])
def getcurrentstat():
    stat = Statistics.query.order_by(Statistics.id.desc()).first()
    return jsonify({
        "temp": stat.temp,
        "humid": stat.humid,
        "dirt_humid": stat.dirt_humid,
        "time": stat.time
    })

@app.route('/menu')
def menuView():
    menu = Menu.query.all()
    return render_template('menu.html', menu=menu)


@app.route('/menuDashboard', methods=['GET', 'POST'])
def menu_def():
    form = UploadMenu()
    if form.validate_on_submit():
        menu = Menu()
        menu.title = form.title.data
        menu.content = form.content.data
        menu.date = datetime.today()
        id_item = str(uuid1())
        menu.uuid = id_item
        form.thumbnail.data.save(f'static/thumbnails/{id_item}.png')
        try:
            db.session.add(menu)
            db.session.commit()
            flash('Complete', 'success')
            return redirect('/menu')
        except Exception as e:
            db.session.rollback()
            print(str(e))
            flash('Failed', 'danger')
            return redirect('/menuDashboard')
    return render_template('menuDashboard.html', form=form)