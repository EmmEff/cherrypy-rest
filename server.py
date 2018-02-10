#!/usr/bin/env python

# pylint: disable=invalid-name

"""
CherryPy-based webservice daemon with background threads
"""

from __future__ import print_function
import threading
import json
import cherrypy
from cherrypy.lib import auth_basic
import cherrypy_cors
from cherrypy.process import plugins
from marshmallow import Schema, fields


USERS = {
    'user': 'password',
}

sample_nodes = [
    'node1',
    'node2',
]


class NodeSchema(Schema):
    name = fields.String(required=True)


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

    print('hello')


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
    def get_all(self):
        # Regular request for '/nodes' URI
        return [{'name': name} for name in sample_nodes]

    @cherrypy.tools.json_out()
    def get(self, name):
        # Handle a GET for a specific node

        if name not in sample_nodes:
            raise cherrypy.HTTPError(
                404, 'Node \"{0}\" not found'.format(name))

        return [{'name': name}]

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def add_node(self):
        # Handle a nodes create request. It might be preferred to
        # create a separate "action" for this controller as opposed
        # to overriding this handler.

        request_data = cherrypy.request.json

        data, errors = NodeSchema().load(request_data)

        if errors:
            # Attempt to format errors dict from Marshmallow
            errmsg = ', '.join(
                ['Key: [{0}], Error: {1}'.format(key, error)
                 for key, error in errors.items()])

            raise cherrypy.HTTPError(
                400, 'Malformed POST request data: {0}'.format(errmsg))

        # Successful POST request
        return 'TODO: add node [{0}]'.format(data['name'])

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_node(self, name):
        if name not in sample_nodes:
            raise cherrypy.HTTPError(
                404, 'Node \"{0}\" not found'.format(name))

        # Empty response (http status 204) for successful PUT request
        cherrypy.response.status = 204

        return ''

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete_node(self, name):
        # Empty response (http status 204) for successful DELETE request
        cherrypy.response.status = 204

        return ''


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


def validate_password(realm, username, password):
    return username in USERS and USERS[username] == password


if __name__ == '__main__':
    cherrypy_cors.install()

    MyBackgroundThread(cherrypy.engine).subscribe()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # /nodes (GET)
    dispatcher.connect(name='nodes',
                       route='/nodes',
                       action='get_all',
                       controller=NodesController(),
                       conditions={'method': ['GET']})

    # /nodes/{name} (GET)
    #
    # Request "/nodes/notfound" (GET) to test the 404 (not found) handler
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='get',
                       controller=NodesController(),
                       conditions={'method': ['GET']})

    # /nodes/{name} (POST)
    dispatcher.connect(name='nodes',
                       route='/nodes',
                       action='add_node',
                       controller=NodesController(),
                       conditions={'method': ['POST']})

    # /nodes/{name} (PUT)
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='update_node',
                       controller=NodesController(),
                       conditions={'method': ['PUT']})

    # /nodes/{name} (DELETE)
    dispatcher.connect(name='nodes',
                       route='/nodes/{name}',
                       action='delete_node',
                       controller=NodesController(),
                       conditions={'method': ['DELETE']})

    config = {
        '/': {
            'request.dispatch': dispatcher,
            'error_page.default': jsonify_error,
            'cors.expose.on': True,
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': 'localhost',
            'tools.auth_basic.checkpassword': validate_password,
        },
    }

    cherrypy.tree.mount(root=None, config=config)

    cherrypy.config.update({
        # 'server.socket_host': '0.0.0.0',
        # 'server.socket_port': 8080,
    })

    cherrypy.engine.start()
    cherrypy.engine.block()
