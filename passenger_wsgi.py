"""cPanel/Passenger entry point.

cPanel uses Phusion Passenger to run Python apps. Passenger expects a WSGI
application object named `application`. Since FastAPI is ASGI (not WSGI),
we use a2wsgi to bridge the gap.

Install: pip install a2wsgi
"""

from a2wsgi import ASGIMiddleware

from backend.main import app

# Passenger looks for a variable named `application`
application = ASGIMiddleware(app)
