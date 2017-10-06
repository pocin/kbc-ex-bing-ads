from exbingads.utils import parse_config

def test_parsing_config():
    params = parse_config('/src/tests/data')
    assert len(params) == 1
    assert isinstance(params, dict)
    assert params['apikey'] == 'foo'

