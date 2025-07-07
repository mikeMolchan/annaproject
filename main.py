from flask import Flask, render_template, request, redirect, url_for

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Date

from flask_apscheduler import APScheduler

import datetime as dt
import requests

API_KEY = 'ab78b2973ee530ac2782f55e027a20f4-c5ea400f-893fc5ef'
DOMAIN = 'mg.noreplywp.com'
RECIPIENTS = ['mikke.molchan@gmail.com']
ACTIONS = ['День Рождения', 'заканчивается отпуск', 'начинается отпуск', 'истекает контракт']



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
# with app.app_context():
#     db.create_all()

class AddEmployeeForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    position = StringField('Должность', validators=[Optional()])
    birthday = DateField('Дата рождения', validators=[Optional()])
    vacation_start = DateField('Начало отпуска', validators=[Optional()])
    vacation_end = DateField('Конец отпуска', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    contract = DateField('Истечение контракта', validators=[Optional()])
    submit = SubmitField('Добавить', validators=[Optional()])






@app.route('/', methods=["GET", "POST"])
def home():
    delete_expired_vacation()
    form = AddEmployeeForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if not check_if_exists(form.name.data) and form.name.data:
                add_employee(form.name.data, form.position.data, form.birthday.data, form.vacation_start.data, form.vacation_end.data, form.email.data, form.contract.data)
                return redirect(url_for('edit'))
            else:
                return render_template('edit.html', form=form, employees=get_employees(), already_exists=True)


    return render_template('index.html', form=form, employees=get_employees(), vacation_now=vacation_now(), contract_soon=contract_soon(), birthday_soon=birthday_soon(), vacation_soon=vacation_soon())



@app.route('/edit', methods=["GET", "POST"])
def edit():
    delete_expired_vacation()
    form = AddEmployeeForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if not check_if_exists(form.name.data) and form.name.data:
                add_employee(form.name.data, form.position.data, form.birthday.data, form.vacation_start.data, form.vacation_end.data, form.email.data, form.contract.data)
                form = AddEmployeeForm(formdata=None)
                return render_template('edit.html', form=form, employees=get_employees())
            else:
                return render_template('edit.html', form=form, employees=get_employees(), already_exists=True)

    return render_template('edit.html', form=form, employees=get_employees())

@app.route("/update_vacation_start", methods=["POST"])
def update_vacation_start():
    employee_id = request.form.get("id")
    new_date_str = request.form.get("vacation_start")

    if not employee_id or not new_date_str:
        return redirect(url_for("edit"))

    employee = db.session.get(Employee4, int(employee_id))
    if employee:
        employee.vacation_start = dt.datetime.strptime(new_date_str, "%Y-%m-%d").date()
        db.session.commit()

    return redirect(url_for("edit"))

@app.route("/update_vacation_end", methods=["POST"])
def update_vacation_end():
    employee_id = request.form.get("id")
    new_date_str = request.form.get("vacation_end")

    if not employee_id or not new_date_str:
        return redirect(url_for("edit"))

    employee = db.session.get(Employee4, int(employee_id))
    if employee:
        employee.vacation_end = dt.datetime.strptime(new_date_str, "%Y-%m-%d").date()
        db.session.commit()

    return redirect(url_for("edit"))

@app.route("/update_contract", methods=["POST"])
def update_contract():
    employee_id = request.form.get("id")
    new_date_str = request.form.get("contract")

    if not employee_id or not new_date_str:
        return redirect(url_for("edit"))

    employee = db.session.get(Employee4, int(employee_id))
    if employee:
        employee.contract = dt.datetime.strptime(new_date_str, "%Y-%m-%d").date()
        db.session.commit()

    return redirect(url_for("edit"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete_employee(id):
    with app.app_context():
        employee = db.session.get(Employee4, id)
        if employee:
            db.session.delete(employee)
            db.session.commit()
    return redirect(url_for("edit"))



'''DB actions'''
def add_employee(name: str, position: str = None, birthday: str = None, vacation_start: str = None, vacation_end: str = None, email: str = None, contract: str = None) -> None:
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


def delete_expired_vacation() -> None:
    employees = get_employees()
    for employee in employees:
        if employee.vacation_start and employee.vacation_end:
            if find_timedelta(employee.vacation_end) < 0:
                with app.app_context():
                    employee1 = db.session.get(Employee4, int(employee.id))
                    employee1.vacation_start = None
                    employee1.vacation_end = None
                    db.session.commit()
    


'''Events actions'''
def find_timedelta(date) -> int:
    return (date - dt.datetime.now().date()).days

def find_timedelta_month(date) -> int:
    return (date - dt.datetime.now().date()).month

def vacation_now() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if employee.vacation_start and employee.vacation_end:
            if find_timedelta(employee.vacation_end) > 0 and find_timedelta(employee.vacation_start) < 0:
                result.append([employee.name, find_timedelta(employee.vacation_end), employee.vacation_end])
        else:
            continue
    return result

def vacation_soon() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if employee.vacation_start:
            if find_timedelta(employee.vacation_start) <= 14 and find_timedelta(employee.vacation_start) > 1:
                result.append([employee.name, find_timedelta(employee.vacation_start), employee.vacation_start])
        else:
            pass
    return result

def birthday_soon() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if employee.birthday:
            if find_timedelta(employee.birthday) < 7:
                result.append([employee.name, find_timedelta(employee.birthday), employee.birthday])
        else:
            continue
    return result

def contract_soon() -> list[list]:
    employees = get_employees()
    result = []
    for employee in employees:
        if employee.contract:
            if find_timedelta(employee.contract) <= 180:
                result.append([employee.name, find_timedelta(employee.contract), employee.contract])
        else:
            continue
    return result

def check_events() -> dict[str: list[tuple]]:
    events = {
        'contract_soon': [],
        'birthday_soon': [],
        'vacation_soon': []
    }

    for employee in contract_soon():
        if employee[1] == 60:
            events['contract_soon'].append((employee[0], employee[1], employee[2]))

    for employee in birthday_soon():
        if employee[1] == 3 or employee[1] == 0:
            events['birthday_soon'].append((employee[0], employee[1], employee[2]))

    for employee in vacation_soon():
        if employee[1] == 14:
            events['vacation_soon'].append((employee[0], employee[1], employee[2]))
    return events
            

    





'''Email actions'''

def send_email(name, days, date, action):
    if days != 0:
        text = f'У сотрудника {name} {action} через {days} дней - {date.strftime("%d.%m.%Y")}'
        subject = f'{action.capitalize()} через {days} дней!'
    else:
        text = f'У сотрудника {name} сегоня День Рождения'
        subject = 'День Рождения сегодня!'
    return requests.post(
        f"https://api.mailgun.net/v3/{DOMAIN}/messages",
        auth=("api", API_KEY),
        data={
            "from": f"Dizzain.com - Сотрудники <mailgun@{DOMAIN}>",
            "to": RECIPIENTS[0],
            "subject": subject,
            "text": text
        }
    )



@scheduler.task('interval', id='every_second', seconds=60)
def job():
    with app.app_context():
        if dt.datetime.now().hour == 14 and dt.datetime.now().minute == 34:
            events = check_events()
            for birthday in events['birthday_soon']:
                    send_email(birthday[0], birthday[1], birthday[2], 'День Рождения')

            for contract in events['contract_soon']:
                    send_email(contract[0], contract[1], contract[2], 'истечение контракта')

            for vacation in events['vacation_soon']:
                    send_email(vacation[0], vacation[1], vacation[2], 'отпуск')

# print(check_events())

if __name__ == '__main__':
    app.run(debug=True)