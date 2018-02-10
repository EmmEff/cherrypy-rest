# cherrypy-rest
Sample implementation of a CherryPy REST API server

Input/output format is JSON

## Usage ##

Run `./server.py`

In another shell session, use `curl` or `wget` to issue URI requests.

Since the example uses HTTP Basic authentication, it is necessary to
specify the user as `user` and password as `password`. This can be seen
in the code under the `import` statements.

For example, to request all nodes:

    curl --verbose --user user:password localhost:8080/nodes

or trigger the 404 (not found) error handler:

    curl --verbose --user user:password localhost:8080/nodes/notfound

or simulate a node creation POST request:

    curl --verbose --user user:password \
        --header "Content-Type: application/json" \
        --data "{\"name\": \"blah\"}" localhost:8080/nodes

or simulate node update (PUT) request:

    curl --verbose --header "Content-Type: application/json" \
        --request PUT --data "{}" localhost:8080/nodes/blah

## Unit tests

Simple unit test for Marshmallow-based schema is available in `test_schema.py`.

Invoke it as follows:

    pytest -sv test_schema.py
