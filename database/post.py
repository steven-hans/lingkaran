from database.content import Content
from main import db


class Post(Content, db.Model):
    __tablename__ = 'post'
    post_number = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    thread_anchor = db.Column(db.Integer, db.ForeignKey('thread.thread_number'))

    content_rel = db.relationship('Content', foreign_keys=post_number)

    def __init__(self, id: int, name: str, ip: str, content: str, date_post: str, thread_anchor: int, media_link: str=''):
        super().__init__(id, name, ip, content, date_post, media_link)
        self.thread_anchor = thread_anchor
        self.post_number = id
