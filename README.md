# cherrypy-rest
Sample implementation of a CherryPy REST API server

Input/output format is JSON

## Usage ##

Run `./server.py`

In another shell session, use `curl` or `wget` to issue URI requests.

For example, to request all nodes:

    curl -v localhost:8080/nodes

or trigger the 404 (not found) error handler:

    curl -v localhost:8080/nodes/notfound

or simulate a node creation POST request:

    curl -v -H "Content-Type: application/json" -d "{}" localhost:8080/nodes/blah

or simulate node update (PUT) request:

    curl -v -H "Content-Type: application/json" -X PUT -d "{}" localhost:8080/nodes/blah
