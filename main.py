import os
import re
import imghdr

from datetime import datetime

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, render_template, session, redirect, url_for
from flask import g
from flask import request

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

from database import actions
import forms
import moderationtools
from moderationtools import is_admin

migrate = Migrate(app, db)
app.register_blueprint(actions.db_handle)
app.register_blueprint(moderationtools.moderation)

admin_keys = ('',)

app.config.from_object(__name__)

from boto3 import Session

ACCESS_KEY = ''
SECRET_KEY = ''
REGION_NAME = ''
BUCKET_NAME = ''

ses = Session(aws_access_key_id=ACCESS_KEY,
              aws_secret_access_key=SECRET_KEY,
              region_name=REGION_NAME)
s3 = ses.resource('s3')

# TODO implement purge thread in moderationtools


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'Ukuran file melewat batas 1 MB.'


@app.route('/')
@app.route('/<int:fail>')
def main_page(fail=0):
    thread_posts = actions.get_mainpage_threads()
    thread_posts.reverse()

    admin_mode = False

    if 'a' in session:
        admin_mode = session['a']

    if fail:
        err = 'Gagal membuat thread. Pastikan subjek & verifikasi terisi dan file .jpg/.png.'
    else:
        err = None

    return render_template('mainpage.html', thread_posts=thread_posts,
                           form=forms.CreateThread(), err=err, adm=admin_mode)


@app.route('/create_thread', methods=('POST',))
def create_thread():  # post method
    if moderationtools.is_banned(request.remote_addr):
        return "You are banned."

    form = forms.CreateThread()
    if form.validate_on_submit():

        new_thread_id = actions.get_new_id()

        # note: extension is guaranteed .jpg and .png, so this is okay.
        file_extension = form.media.data.filename.split('.')[-1]
        new_file_name = str(int(datetime.now().timestamp()*1000000))+'.'+file_extension

        form.media.data.save('/tmp/file')
        file_length = os.stat('/tmp/file').st_size

        if imghdr.what('/tmp/file') not in ['png', 'jpg', 'jpeg']:
            return 'File harus merupakan .png atau .jpg'

        if file_length > 1024 * 1024:
            return 'File melebihi batas 1 MB.'

        s3.Bucket(BUCKET_NAME).upload_file('/tmp/file', new_file_name)

        # TODO Deletes the object, can be useful. Need to find out how to 'bulk delete' so it's faster
        # obj = s3.Object(BUCKET_NAME, form.media.data.filename)
        # obj.delete()
        # print('delete success')

        name = form.name.data.strip()[:64]
        if len(name) == 0:
            name = 'Anonymous'

        subject = form.subject.data.strip()[:64]
        content = form.content.data.strip()[:1536]
        ip = request.remote_addr
        actions.post_new_thread(name, subject, ip, content, new_file_name)

        return redirect(url_for('view_thread', thread_id=new_thread_id))
    else:
        return redirect(url_for('main_page', fail=1))


@app.template_filter('format_post_reference')
def format_post_reference(post):
    res = []
    for chunk in post.split('>>'):
        match = re.match(r'^(\d+)(.*)', chunk)
        if match:
            res.append(match.groups())
        else:
            res.append((None, chunk,))
    return res


@app.route('/view/<int:thread_id>')
@app.route('/view/<int:thread_id>/<int:fail>')
def view_thread(thread_id, fail=0):  # get method with ID from template
    thread_post = actions.get_thread(thread_id)

    if fail:
        err = 'Gagal membuat thread. Pastikan verifikasi dicentang atau/dan file .jpg/.png.'
    else:
        err = None

    if thread_post.thread_post is None:
        return 'Thread not found.'
    else:
        return render_template('threadview.html', tp=thread_post, reply_count=len(thread_post.posts),
                               form=forms.PostReply(), adm=is_admin(), err=err)


@app.route('/post_reply/<int:thread_anchor>', methods=('POST',))
def post_reply(thread_anchor):  # post method
    if moderationtools.is_banned(request.remote_addr):
        return "You are banned."

    form = forms.PostReply()
    if form.validate_on_submit():
        name = form.name.data.strip()[:64]
        if len(name) == 0:
            name = 'Anonymous'

        new_file_name = ''
        if form.media.has_file():
            file_extension = form.media.data.filename.split('.')[-1]
            new_file_name = str(int(datetime.now().timestamp()*1000000)) + '.' + file_extension
            s3.Bucket(BUCKET_NAME).upload_fileobj(form.media.data, new_file_name)

        new_id = actions.get_new_id()
        content = form.content.data.strip()[:1536]
        actions.post_reply(new_id, thread_anchor, name, request.remote_addr, content, new_file_name)
        return redirect(url_for('view_thread', thread_id=thread_anchor))
    else:
        return redirect(url_for('view_thread', thread_id=thread_anchor, fail=1))


@app.teardown_appcontext
def close_connection(ex):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
