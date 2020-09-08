import json
from datetime import datetime
from unittest import TestCase
from message_api import create_app


app = create_app(config_name="testing")


class MessagesApi(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.client = app.test_client()
        self._sender = "albert"
        self._target = "norbert"
        with app.app_context():
            # create all tables
            from message_api.sqlalquemy_store import db
            db.session.remove()
            db.drop_all()
            db.create_all()

    def test_no_messages_with_clean_start(self):
        res = self.get_messages()
        self.assertEqual([], res)

    def test_post_message(self):
        res = self.post_message('test message 1')

        self.assertIsNotNone(res.get("id"))
        self.assertEqual(self._sender, res.get("sender"))
        self.assertEqual(self._target, res.get("target"))
        self.assertEqual("test message 1", res.get("text"))
        d = res.get("sent_time")
        datetime.fromisoformat(d)

    def test_fail_post_message_no_data(self):
        self.post(
            self.messages_uri(self._target),
            None,
            400)

    def test_fail_post_message_wrong_data_type(self):
        self.post(
            self.messages_uri(self._target),
            [1],
            400)

    def test_fail_post_message_no_sender_user_id(self):
        self.post(
            self.messages_uri(self._target),
            {'text': 'test message 1'},
            400)

    def test_fail_post_message_no_text(self):
        self.post(
            self.messages_uri(self._target),
            {'user_id': 'xxx'},
            400)

    def test_get_posted_message(self):
        self.post_message('test message 1')

        res = self.get_messages()
        self.assertEqual(1, len(res))
        self.assertEqual("test message 1", res[0].get("text"))

    def test_get_posted_message_on_different_user_should_be_empty(self):
        self.post_message('test message 1', target=self._target + "_jr")

        res = self.get_messages()
        self.assertEqual(0, len(res))

    def test_post_message_on_two_users_should_be_empty_get_messages_for_one(self):
        self.post_message('test message 1')

        self.post_message('test message 2', target=self._target + "_jr")

        res = self.get_messages()
        self.assertEqual(1, len(res))
        self.assertEqual("test message 1", res[0].get("text"))

        res = self.get_messages(user_name=self._target + "_jr")

        self.assertEqual(1, len(res))
        self.assertEqual("test message 2", res[0].get("text"))

    def test_multiple_calls_to_get_only_return_new_messages(self):
        self.post_message('test message 1')
        self.post_message('test message 2')

        res = self.get_messages()
        self.assertEqual(2, len(res))
        self.assertEqual("test message 1", res[0].get("text"))
        self.assertEqual("test message 2", res[1].get("text"))

        res = self.get_messages()
        self.assertEqual(0, len(res))

        self.post_message('test message 3')
        self.post_message('test message 4')
        self.post_message('test message 5')

        res = self.get_messages()
        self.assertEqual(3, len(res))
        self.assertEqual("test message 3", res[0].get("text"))
        self.assertEqual("test message 4", res[1].get("text"))
        self.assertEqual("test message 5", res[2].get("text"))

    def test_get_all_returns_every_message_on_multiple_get_calls(self):
        self.post_message('test message 1')
        self.post_message('test message 2')

        res = self.get_messages()
        self.assertEqual(2, len(res))

        self.post_message('test message 3')

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(3, len(res))
        self.assertEqual("test message 1", res[0].get("text"))
        self.assertEqual("test message 2", res[1].get("text"))
        self.assertEqual("test message 3", res[2].get("text"))

    def test_delete_non_existing_message_returns_ok(self):
        deleted_count = self.delete_messages(918273645)
        self.assertEqual(0, deleted_count)

    def test_delete_posted_message(self):
        message = self.post_message('test message 1')

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(1, len(res))

        deleted_count = self.delete_messages(message.get("id"))
        self.assertEqual(1, deleted_count)

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(0, len(res))

    def test_delete_one_of_several_posted_messages(self):
        self.post_message('test message 1')
        message = self.post_message('test message 2')
        self.post_message('test message 3')

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(3, len(res))

        deleted_count = self.delete_messages(message.get("id"))
        self.assertEqual(1, deleted_count)

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(2, len(res))
        self.assertEqual("test message 1", res[0].get("text"))
        self.assertEqual("test message 3", res[1].get("text"))

    def test_delete_message_for_non_matching_user(self):
        message = self.post_message('test message 1')

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(1, len(res))

        deleted_count = self.delete_messages(message.get("id"), target=self._target + "_jr")
        self.assertEqual(0, deleted_count)

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(1, len(res))
        self.assertEqual("test message 1", res[0].get("text"))
        self.assertEqual(self._target, res[0].get("target"))

    def test_multiple_delete_of_some_posted_message(self):
        self.post_message('test message 1')
        message1 = self.post_message('test message 2')
        self.post_message('test message 3')
        message2 = self.post_message('test message 4')

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(4, len(res))

        deleted_count = self.delete_messages(message1.get("id"), message2.get("id"))
        self.assertEqual(2, deleted_count)

        res = self.get_messages(get_old_messages=True)
        self.assertEqual(2, len(res))
        self.assertEqual("test message 1", res[0].get("text"))
        self.assertEqual("test message 3", res[1].get("text"))

    def test_fail_delete_with_wrong_data(self):
        self.delete(
            self.messages_uri(self._target),
            400,
            data={})

    def post_message(self, text, target=None):
        return self.post(
            self.messages_uri(target or self._target),
            self.make_message(text),
            201)

    def get_messages(self, user_name=None, get_old_messages=None):
        return self.get(self.messages_uri(
            user_name=user_name or self._target,
            get_old_messages=get_old_messages),
            200)

    def delete_messages(self, *message_ids, target=None):

        res = self.delete(
            self.messages_uri(target or self._target, message_id=message_ids[0] if len(message_ids) == 1 else None),
            200,
            data=list(message_ids) if len(message_ids) > 1 else None)
        return res.get("deleted_count")

    @staticmethod
    def messages_uri(user_name, message_id=None, get_old_messages=False):
        uri = f'/users/{ user_name }/messages'
        if message_id:
            uri += f'/{message_id}'

        query_string = []
        if get_old_messages:
            query_string.append(f'get_old_messages={str(get_old_messages).lower()}')

        if query_string:
            uri += '?' + '&'.join(query_string)

        return uri

    def make_message(self, message):
        return {'user_id': self._sender, 'text': message}

    def post(self, uri, data, status_code):
        res = self.client.post(uri, data=json.dumps(data))
        self.assertEqual(status_code, res.status_code)

        return json.loads(res.data)

    def delete(self, uri, status_code, data=None):
        res = self.client.delete(uri, data=json.dumps(data) if data is not None else None)
        self.assertEqual(status_code, res.status_code)

        return json.loads(res.data)

    def get(self, uri, status_code):
        res = self.client.get(uri)
        self.assertEqual(res.status_code, status_code)

        return json.loads(res.data)
