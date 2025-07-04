from flask import Flask, render_template

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
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



class Employee(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True,  autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    position: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    birthday: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    vacation: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    contract: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
 

# Create table schema in the db
# !Comment after creating a table!
# with app.app_context():
#     db.create_all()

class AddEmployeeForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    birthday = StringField('Дата рождения', validators=[DataRequired()])
    vacation = StringField('Отпуск', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    contract = StringField('Истечение контракта', validators=[DataRequired()])
    submit = SubmitField('Добавить')



    



@app.route('/', methods=["GET", "POST"])
def home():
    form = AddEmployeeForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            add_employee(form.name.data, form.position.data, form.birthday.data, form.vacation.data, form.email.data, form.contract.data)
            return render_template('index.html', form=form, employees=get_employees())
    return render_template('index.html', form=form, employees=get_employees())






def add_employee(name: str, position: str, birthday: str, vacation: str = 'None', email: str = 'None', contract: str = 'None') -> None:
    with app.app_context():
        employee = Employee(name=name, position=position, birthday=birthday, vacation=vacation, email=email, contract=contract)
        db.session.add(employee)
        db.session.commit()


def get_employees() -> tuple[object]:
    with app.app_context():
        employees = Employee.query.all()
        # db.session.commit()
    return employees

    





if __name__ == '__main__':
    app.run(debug=True)