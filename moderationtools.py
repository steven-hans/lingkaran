from flask import Blueprint
from flask import session, render_template, request, redirect

import forms
from database import actions
from main import db
from database.bannedips import BannedIPs
from database.content import Content

import main

moderation = Blueprint('moderation', __name__, template_folder='templates')


def is_admin():
    return 'a' in session and session['a']


@moderation.route('/remove_thread/<int:thread_id>')
def remove_thread(thread_id):
    if 'a' in session and session['a']:
        actions.delete_thread(thread_id)
    else:
        print('Failed to delete thread', thread_id, 'by', request.remote_addr)

    return main.main_page()


@moderation.route('/remove_post/<int:post_id>/<int:thread_anchor>')
def remove_post(post_id, thread_anchor):
    if is_admin():
        actions.delete_post(post_id)

    return main.view_thread(thread_anchor)


@moderation.route('/admin_panel')
def admin_panel():
    form = forms.AdminPanel()
    return render_template('adminpanel.html', form=form)


@moderation.route('/admin_login', methods=('POST',))
def admin_login():
    form = forms.AdminPanel()
    if form.validate_on_submit():
        key = form.key.data.strip()
        if key in main.admin_keys:
            session['a'] = True
            return main.main_page()
        else:
            return 'Invalid login'


@moderation.route('/ban_ip_from/<int:content_id>')
def ban_ip(content_id):
    if is_admin():
        ip = db.session.query(Content).filter(Content.id == content_id).first().ip
        banned_ip = BannedIPs(ip)
        db.session.add(banned_ip)
        db.session.commit()
        print('Banning ip', ip)

    return main.main_page()


@moderation.route('/unban_ip/<string:ip>')
def unban_ip(ip):
    if is_admin():
        BannedIPs.query.filter(BannedIPs.ip == ip).delete()
        db.session.commit()
        return 'ok'

    return redirect(request.referrer)


def is_banned(ip):
    ip_exists = db.session.query(BannedIPs).filter(BannedIPs.ip == ip).first()
    return ip_exists is not None
