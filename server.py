#!/usr/bin/env python

# pylint: disable=invalid-name

"""
CherryPy-based webservice daemon with background threads
"""

import threading
import json
import cherrypy
from cherrypy.process import plugins


def worker():
    """Background Timer that runs the hello() function every 5 seconds

    TODO: this needs to be fixed/optimized. I don't like creating the thread
    repeatedly.
    """

    while True:
        t = threading.Timer(5.0, hello)
        t.start()
        t.join()


def hello():
    """Output 'hello' on the console"""

    print 'hello'


class MyBackgroundThread(plugins.SimplePlugin):
    """CherryPy plugin to create a background worker thread"""

    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)

        self.t = None

    def start(self):
        """Plugin entrypoint"""

        self.t = threading.Thread(target=worker)
        self.t.daemon = True
        self.t.start()

    # Start at a higher priority that "Daemonize" (which we're not using
    # yet but may in the future)
    start.priority = 85


class NodesController(object): \
        # pylint: disable=too-few-public-methods

    """Controller for fictional "nodes" webservice APIs"""

    @cherrypy.tools.json_out()
    def nodes(self, name=None):
        """
        /nodes (GET)
        /nodes/<name> (GET)
        /nodes/<name> (POST)
        """

        if cherrypy.request.method == 'POST':
            # Handle a nodes create request. It might be preferred to
            # create a separate "action" for this controller as opposed
            # to overriding this handler.

            if not name:
                # We have to explicitly check for the 'name' argument
                # because this is an overriden controller and name=None
                # is a valid option for the GET method.

                raise cherrypy.HTTPError(
                    400, 'Missing node \'name\' argument')

            # Successful POST request
            return ('You\'re wanting to create a node named'
                    ' \"{0}\"?'.format(name))

        elif cherrypy.request.method == 'PUT':
            # Handle PUT method for record updates

            if not name:
                raise cherrypy.HTTPError(
                    400, 'Missing node \'name\' argument')

            return 'Request to update node \"{0}\"'.format(name)

        if name:
            # Handle a GET for a specific node

            if name == 'notfound':
                raise cherrypy.HTTPError(
                    404, 'Node \"{0}\" not found'.format(name))

            return 'You requested the node \"{0}\"'.format(name)

        # Regular request for '/nodes' URI
        return 'hello there: id=%r' % (id(self))


def jsonify_error(status, message, traceback, version): \
        # pylint: disable=unused-argument

    """JSONify all CherryPy error responses (created by raising the
    cherrypy.HTTPError exception)
    """

    cherrypy.response.headers['Content-Type'] = 'application/json'
    response_body = json.dumps(
        {
            'error': {
                'http_status': status,
                'message': message,
            }
        })

    cherrypy.response.status = status

    return response_body


if __name__ == '__main__':
    MyBackgroundThread(cherrypy.engine).subscribe()

    d = cherrypy.dispatch.RoutesDispatcher()

    # /nodes (GET)
    d.connect(name='nodes', route='/nodes', action='nodes',
              controller=NodesController())

    # /nodes/{name} (GET)
    # /nodes/{name} (POST)
    # /nodes/{name} (PUT)
    #
    # Request "/nodes/notfound" (GET) to test the 404 (not found) handler
    d.connect(name='nodes', route='/nodes/{name}', action='nodes',
              controller=NodesController(),
              conditions={'method': ['GET', 'POST', 'PUT']})

    config = {
        'global': {
            'server.socket_host': '0.0.0.0',
            # 'server.socket_port': 8080,
        },
        '/': {
            'request.dispatch': d,
            'error_page.default': jsonify_error,
        },
    }

    cherrypy.tree.mount(root=None, config=config)

    cherrypy.engine.start()
    cherrypy.engine.block()
