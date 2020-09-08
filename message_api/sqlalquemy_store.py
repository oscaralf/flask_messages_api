from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import current_app as app

db = SQLAlchemy()
ma = Marshmallow()


# def register_app(app):
db.init_app(app)
ma.init_app(app)
db.create_all()


def add_message(sender_user_id, target_user_id, text):
    new_message = UserMessageModel(sender_user_id, target_user_id, text, datetime.utcnow())
    db.session.add(new_message)
    db.session.commit()
    return user_message_schema.dump(new_message)


def get_messages(user_id, get_old_messages=False):

    messages_filter = UserMessageModel.query.filter_by(target=user_id)

    if not get_old_messages:
        user_data = UserModel.query.filter_by(user_id=user_id).first()
        if user_data and user_data.last_message_read_timestamp:
            messages_filter = messages_filter.filter(UserMessageModel.sent_time > user_data.last_message_read_timestamp)

    messages = messages_filter.all()

    latest_message = max(messages, key=lambda x: x.sent_time, default=None)
    if latest_message and latest_message.sent_time:
        _set_last_read_timestamp(user_id, latest_message.sent_time)

    return user_messages_schema.dump(messages)


def delete_message(user_id, *message_ids):
    deleted_count = db.session.query(UserMessageModel)\
        .filter_by(target=user_id)\
        .filter(UserMessageModel.id.in_(message_ids))\
        .delete(synchronize_session=False)

    db.session.commit()
    return deleted_count


def _set_last_read_timestamp(user_id, timestamp):
    user_data = UserModel.query.filter_by(user_id=user_id).first()
    if not user_data:
        user_data = UserModel(user_id, last_message_read_timestamp=timestamp)
        db.session.add(user_data)
    else:
        user_data.last_message_read_timestamp = timestamp
    db.session.commit()


USER_ID_LEN = 100


class UserMessageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(USER_ID_LEN), nullable=False)
    target = db.Column(db.String(USER_ID_LEN), nullable=False)
    text = db.Column(db.Text, nullable=False)
    sent_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, sender, target, text, sent_time):
        self.sender = sender
        self.target = target
        self.text = text
        self.sent_time = sent_time


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(USER_ID_LEN), nullable=False)
    last_message_read_timestamp = db.Column(db.DateTime, nullable=True)

    def __init__(self, user_id, last_message_read_timestamp=None):
        self.user_id = user_id
        self.last_message_read_timestamp = last_message_read_timestamp


class UserMessageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'sender', 'target', 'text', 'sent_time')


user_message_schema = UserMessageSchema()
user_messages_schema = UserMessageSchema(many=True)
