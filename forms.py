from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (BooleanField, EmailField, PasswordField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length


class RegisterForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired(), Length(min=2, max=40)])
    pwd = PasswordField("Пароль", validators=[DataRequired(), Length(min=4)])
    pwd2 = PasswordField("Повторите пароль",
                         validators=[DataRequired(),
                                     EqualTo("pwd", message="Пароли не совпадают")])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    pwd = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class PostForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(max=120)])
    text = TextAreaField("Текст", validators=[DataRequired()])
    image = FileField("Картинка",
                      validators=[FileAllowed(["jpg", "jpeg", "png", "gif"],
                                              "Только картинки")])
    submit = SubmitField("Сохранить")
