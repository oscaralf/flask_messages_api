from flask import current_app as app
from healthcheck import HealthCheck, EnvironmentDump

health = HealthCheck()
env_dump = EnvironmentDump()

app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())
app.add_url_rule("/environment", "environment", view_func=lambda: env_dump.run())
