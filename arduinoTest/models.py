from arduino import db


# describe db model
class Data(db.Model):
    __tablename__ = "data"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    temperature = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)

    def __init__(self, temperature, humidity, timestamp):
        self.temperature = temperature
        self.humidity = humidity
        self.timestamp = timestamp

    def __repr__(self):
        return "<User %r>" % self.temperature
