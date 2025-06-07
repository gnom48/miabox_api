"""
This script runs the application using a development server.
"""

import bottle
from bottle import TEMPLATE_PATH
if __name__ == '__main__':
    import routes
else:
    import app.routes


TEMPLATE_PATH.insert(0, './app/views')

app = bottle.app()

if __name__ == '__main__':
    # local/debug by python
    bottle.run(app=app, host='localhost', port='8084')
