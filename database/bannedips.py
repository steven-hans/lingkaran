from main import db


class BannedIPs(db.Model):
    __tablename__ = 'bannedips'
    ip = db.Column(db.String(16), primary_key=True)

    def __init__(self, ip):
        self.ip = ip