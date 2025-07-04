from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

app = Flask(__name__)
app.secret_key = 'dizzaincom2025%'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


# Creates a basic class
class Base(DeclarativeBase):
    pass


# Creates the db
db = SQLAlchemy(model_class=Base)
# Binds the db with flask app
db.init_app(app)



class Employee1(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True,  autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    position: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    birthday: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    vacation_start: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    vacation_end: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    contract: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
 

# Create table schema in the db
# !Comment after creating a table!
# with app.app_context():
#     db.create_all()

class AddEmployeeForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    position = StringField('Должность')
    birthday = StringField('Дата рождения')
    vacation_start = StringField('Начало отпуска')
    vacation_end = StringField('Конец отпуска')
    email = StringField('Email')
    contract = StringField('Истечение контракта')
    submit = SubmitField('Добавить')






@app.route('/', methods=["GET", "POST"])
def home():
    form = AddEmployeeForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if not check_if_exists(form.name.data):
                add_employee(form.name.data, form.position.data, form.birthday.data, form.vacation_start.data, form.vacation_end.data, form.email.data, form.contract.data)
            else:
                if form.vacation_start.data and form.vacation_start.data:
                    update_vacation_by_name(form.name.data, form.vacation_start.data, form.vacation_end.data)
                elif form.contract.data:
                    update_contract_by_name(form.name.data, form.contract.data)
                else:
                    pass

            return render_template('index.html', form=form, employees=get_employees())
    return render_template('index.html', form=form, employees=get_employees())








def add_employee(name: str, position: str = 'None', birthday: str = 'None', vacation_start: str = 'None', vacation_end: str = 'None', email: str = 'None', contract: str = 'None') -> None:
    with app.app_context():
        employee = Employee1(name=name, position=position, birthday=birthday, vacation_start=vacation_start, vacation_end=vacation_end, email=email, contract=contract)
        db.session.add(employee)
        db.session.commit()


def get_employees() -> tuple[object]:
    with app.app_context():
        employees = Employee1.query.all()
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
        employee = Employee1.query.filter_by(name=name).first()
        if employee:
            employee.vacation_start = vacation_start
            employee.vacation_end = vacation_end
            db.session.commit()

def update_contract_by_name(name: str, contract: str) -> None:
    with app.app_context():
        employee = Employee1.query.filter_by(name=name).first()
        if employee:
            employee.contract = contract
            db.session.commit()
    

print(check_if_exists)


if __name__ == '__main__':
    app.run(debug=True)