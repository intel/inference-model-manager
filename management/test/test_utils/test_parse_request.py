from management_api.utils.parse_request import get_params
import pytest
import falcon


@pytest.mark.parametrize("raise_error, body", [(False, {'test': '', 'default': ''}),
                                               (True, {'test': '', 'ns': ''}),
                                               (True, {'api': '', 'default': ''}),
                                               (True, {'api': '', 'ns': ''})])
def test_get_params(raise_error, body):
    required_keys = ['test', 'default']
    if raise_error:
        with pytest.raises(falcon.HTTPBadRequest):
            get_params(body=body, required_keys=required_keys)
    else:
        get_params(body=body, required_keys=required_keys)