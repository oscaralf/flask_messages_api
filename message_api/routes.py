import os

import markdown
from flask import current_app as app, request, abort
from flask_restful import Resource
from message_api.sqlalquemy_store import add_message, get_messages, delete_message


@app.route('/')
def index():
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)


class MessageList(Resource):

    @staticmethod
    def get(user_id):
        get_old_messages = request.args.get("get_old_messages")
        if get_old_messages not in (None, "true", "false"):
            abort(400, "'get_old_messages' must be [true|false]")

        get_old_messages = get_old_messages == 'true'

        page = request.args.get("page")
        page_size = request.args.get("page_size")

        if page is not None or page_size is not None:
            if not get_old_messages:
                abort(400, "Pagination parameters [page|page_size] can only be used when 'get_old_messages=true'")

            page = page or 0
            page_size = page_size or 10

            try:
                page = int(page)
                page_size = int(page_size)
            except ValueError:
                abort(400, "'page' and 'page_size' must be integers")

        messages = get_messages(
            user_id,
            get_old_messages=get_old_messages,
            page=page,
            page_size=page_size)
        return messages, 200

    @staticmethod
    def post(user_id):
        request_data = request.get_json(force=True)
        if not isinstance(request_data, dict):
            abort(400, "JSON data must be an object")

        target_user_id = user_id
        sender_user_id = request_data.get('user_id')
        text = request_data.get('text')

        if not sender_user_id:
            abort(400, 'Missing "user_id"')

        if not text:
            abort(400, 'Missing "text"')

        return add_message(
            sender_user_id,
            target_user_id,
            text,
        ), 201

    @staticmethod
    def delete(user_id):
        request_data = request.get_json(force=True)

        if not isinstance(request_data, list):
            abort(400, 'JSON data must be an array with "message_id"')

        request_data = [str(x) for x in request_data]

        deleted_count = delete_message(user_id, *request_data)
        return {'deleted_count': deleted_count}, 200


class Message(Resource):
    @staticmethod
    def delete(user_id, message_id):

        deleted_count = delete_message(user_id, message_id)
        return {'deleted_count': deleted_count}, 200


app.api.add_resource(MessageList, '/users/<string:user_id>/messages')
app.api.add_resource(Message, '/users/<string:user_id>/messages/<string:message_id>')
