from database.content import Content
from main import db


class Thread(Content, db.Model):
    __tablename__ = 'thread'
    subject = db.Column(db.String(64))
    thread_number = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    pinned = db.Column(db.Boolean)
    locked = db.Column(db.Boolean)

    content_rel = db.relationship('Content', foreign_keys=thread_number)

    def __init__(self, id, name, ip, content, date_post, subject, pinned, locked, media_link):
        super().__init__(id, name, ip, content, date_post, media_link)
        self.thread_number = id
        self.pinned = pinned
        self.locked = locked
        self.subject = subject
