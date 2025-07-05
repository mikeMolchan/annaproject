from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Date

from flask_apscheduler import APScheduler

import datetime as dt

app = Flask(__name__)
app.secret_key = 'dizzaincom2025%'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


# Creates a basic class
class Base(DeclarativeBase):
    pass


# Creates the db
db = SQLAlchemy(model_class=Base)
# Binds the db with flask app
db.init_app(app)



class Employee4(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    position: Mapped[str] = mapped_column(String(250), nullable=True)
    birthday: Mapped[dt.date] = mapped_column(Date, nullable=True)
    vacation_start: Mapped[dt.date] = mapped_column(Date, nullable=True)
    vacation_end: Mapped[dt.date] = mapped_column(Date, nullable=True)
    email: Mapped[str] = mapped_column(String(250), nullable=True)
    contract: Mapped[dt.date] = mapped_column(Date, nullable=True)
 

# Create table schema in the db
# !Comment after creating a table!
with app.app_context():
    db.create_all()

class AddEmployeeForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    position = StringField('Должность')
    birthday = DateField('Дата рождения')
    vacation_start = DateField('Начало отпуска')
    vacation_end = DateField('Конец отпуска')
    email = StringField('Email')
    contract = DateField('Истечение контракта')
    submit = SubmitField('Добавить')






@app.route('/', methods=["GET", "POST"])
def home():
    form = AddEmployeeForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if not check_if_exists(form.name.data):
                print(1)
                add_employee(form.name.data, form.position.data, form.birthday.data, form.vacation_start.data, form.vacation_end.data, form.email.data, form.contract.data)
            else:
                if form.vacation_start.data and form.vacation_start.data:
                    print(2)
                    update_vacation_by_name(form.name.data, form.vacation_start.data, form.vacation_end.data)
                elif form.contract.data:
                    print(3)
                    update_contract_by_name(form.name.data, form.contract.data)
                else:
                    print(4)
                    pass

            return render_template('index.html', form=form, employees=get_employees(), vacation_now=vacation_now(), contract_soon=contract_soon(), birthday_soon=birthday_soon(), vacation_soon=vacation_soon())
    return render_template('index.html', form=form, employees=get_employees(), vacation_now=vacation_now(), contract_soon=contract_soon(), birthday_soon=birthday_soon(), vacation_soon=vacation_soon())








def add_employee(name: str, position: str = 'None', birthday: str = 'None', vacation_start: str = 'None', vacation_end: str = 'None', email: str = 'None', contract: str = 'None') -> None:
    with app.app_context():
        employee = Employee4(name=name, position=position, birthday=birthday, vacation_start=vacation_start, vacation_end=vacation_end, email=email, contract=contract)
        db.session.add(employee)
        db.session.commit()


def get_employees() -> tuple[object]:
    with app.app_context():
        employees = Employee4.query.all()
        # db.session.commit()
    return employees

def check_if_exists(name: str) -> bool:
    employees = get_employees()
    for employee in employees:
        if name == employee.name:
            return True
        else:
            continue
    return False

def update_vacation_by_name(name: str, vacation_start: str, vacation_end: str) -> None:
    with app.app_context():
        employee = Employee4.query.filter_by(name=name).first()
        if employee:
            employee.vacation_start = vacation_start
            employee.vacation_end = vacation_end
            db.session.commit()

def update_contract_by_name(name: str, contract: str) -> None:
    with app.app_context():
        employee = Employee4.query.filter_by(name=name).first()
        if employee:
            employee.contract = contract
            db.session.commit()
    

def find_timedelta(date) -> int:
    return (date - dt.datetime.now().date()).days

def vacation_now() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if find_timedelta(employee.vacation_end) > 0 and find_timedelta(employee.vacation_start) < 0:
            result.append([employee.name, find_timedelta(employee.vacation_end)])
    return result

def vacation_soon() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if find_timedelta(employee.vacation_start) < 7 and find_timedelta(employee.vacation_start) > 1:
            result.append([employee.name, find_timedelta(employee.vacation_start)])
    return result

def birthday_soon() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if find_timedelta(employee.birthday) < 7:
            result.append([employee.name, find_timedelta(employee.birthday)])
    return result

def contract_soon() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if find_timedelta(employee.contract) < 180 :
            result.append([employee.name, find_timedelta(employee.contract)])
    return result

@scheduler.task('interval', id='every_second', seconds=1)
def job():
    with app.app_context():
        pass


if __name__ == '__main__':
    app.run(debug=True)