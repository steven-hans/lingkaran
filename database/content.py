from main import db
from dateutil.parser import parse


class Content(db.Model):
    __tablename__ = 'content'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    ip = db.Column(db.String(16))
    # Maybe replace \n  with <br> and somehow render it in the browser? or maybe content is rows of text. each new
    # line is that rows of text, then rendering is just content + <br> for each line
    content = db.Column(db.String(1536))
    media_link = db.Column(db.String)
    date_post = db.Column(db.DateTime)

    date_post_epoch = None
    displayed_date = None
    displayed_content = []

    def __init__(self, id=None, name='Anonymous', ip='127.0.0.1', content='', date_post='1990-01-01 00:00', media_link=''):
        self.id = id
        self.name = name
        self.ip = ip
        self.content = content
        self.date_post = date_post
        self.media_link = media_link
        self.set_displayed_date()
        self.set_displayed_content()

    def set_displayed_date(self):
        self.displayed_date = self.date_post.strftime('%y/%m/%d %H:%M')

    def get_date_unix(self):
        if self.date_post_epoch is None:
            self.date_post_epoch = self.date_post.timestamp()
        return self.date_post_epoch

    def set_displayed_content(self):
        self.displayed_content = self.content.split('\n')
