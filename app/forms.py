from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Password Lama', validators=[DataRequired()])
    new_password = PasswordField('Password Baru', validators=[DataRequired()])
    confirm_new_password = PasswordField('Konfirmasi Password Baru', 
    validators=[DataRequired(), EqualTo('new_password', message="Password harus sama")])
    submit = SubmitField('Ganti Password')