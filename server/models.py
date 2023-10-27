from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship('Signup', backref='activity', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "difficulty": self.difficulty
        }

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    signups = db.relationship('Signup', backref='camper', cascade='all, delete-orphan')

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise  ValueError('Name is required')
        return name

    @validates('age')
    def validate_age(self, key, age):
        if age < 8 or age > 18:
            raise ValueError('Age must be between 8 and 18')
        return age
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age
        }

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    @validates('time')
    def validate_time(self, key, time):
        if time < 0 or time > 23:
            raise ValueError('Time must be between 0 and 23')
        return time
    
    def to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "camper_id": self.camper_id,
            "activity_id": self.activity_id,
            "camper": self.camper.to_dict() if self.camper else None,
            "activity": self.activity.to_dict() if self.activity else None
        }

    def __repr__(self):
        return f'<Signup {self.id}>'