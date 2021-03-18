from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, validators


class CreateThread(FlaskForm):
    name = StringField('Nama')
    subject = StringField('Subyek')
    content = TextAreaField('Isi', [validators.Length(min=8)])
    recaptcha = RecaptchaField('Verifikasi')
    media = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'File hanya dapat berupa gambar.')
    ])
    submit = SubmitField('Submit')


class PostReply(FlaskForm):
    name = StringField('Nama')
    content = TextAreaField('Isi')
    recaptcha = RecaptchaField('Verifikasi')
    media = FileField('File')
    submit = SubmitField('Submit')


class AdminPanel(FlaskForm):
    key = StringField('Key')
    submit = SubmitField('Submit')
