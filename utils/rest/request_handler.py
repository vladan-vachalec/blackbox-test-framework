import json


class ValidatableResponse:
    def __init__(self, response, session, expected_result):
        self.response = response
        self.url = response.url
        self.method = response.request.method
        self.request_body = json.loads(response.request.body) if response.request.body else None
        self.headers = session.headers
        self.cookies = session.cookies.get_dict()
        self.content = json.loads(response.content)
        self.pm_status_code = self.content['Code']
        self.http_status_code = response.status_code
        self.expected_result = expected_result

    def __str__(self):
        return '\n'.join([
            '\n',
            'URL: %s' % self.url,
            'Method: %s' % self.method,
            'Headers: %s' % json.dumps(self.headers, indent=4),
            'Cookies: %s' % json.dumps(self.cookies, indent=4),
            'Request Body: %s' % json.dumps(self.request_body, indent=4),
            'Response Body: %s' % json.dumps(self.content, indent=4),
            'Actual Status code  : %s' % self.http_status_code,
            'Expected Status code: %s' % self.expected_result,
        ])


class Borg(object):
    # The borg singleton - https://bit.ly/2zPRSOB
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(Borg, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj


class RequestHandler(Borg):
    def __init__(self, base_uri=None, default_headers=None, session=None):
        Borg.__init__(self)
        if None not in [base_uri, default_headers, session]:
            self.base_uri = base_uri
            self.session = session
            self.session.headers = default_headers

    def do_request(self, method, endpoint, expected_result, body=None, another_session=None):
        session = self.session if not another_session else another_session
        req = session.request(method=method, url=self.base_uri + endpoint, json=body)
        res = ValidatableResponse(req, session=session, expected_result=expected_result)
        assert res.http_status_code == expected_result, res
        return res
