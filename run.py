from os import environ

from message_api import create_app

app = create_app(environ.get('CONFIG_NAME', 'development'))
app.run(host='0.0.0.0', port=int(environ.get('PORT', 8080)), debug=app.config["DEBUG"])
