from server import NodeSchema


def test_basic():
    data, errors = NodeSchema().loads('{\"name\": \"user\"}')

    assert not errors

    assert 'name' in data


def test_missing_name_field():
    data, errors = NodeSchema().loads('{}')

    assert errors

    assert 'name' not in data


def test_missing_name_field2():
    data, errors = NodeSchema().loads('{\"key\": \"value\"}')

    assert errors

    assert 'name' not in data
