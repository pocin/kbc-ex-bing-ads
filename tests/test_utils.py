from exbingads.utils import parse_config

def test_parsing_config():
    params = parse_config('/src/tests/data')
    assert len(params) == 4
    assert isinstance(params, dict)
    assert params['bucket'] == 'out.c-main'

