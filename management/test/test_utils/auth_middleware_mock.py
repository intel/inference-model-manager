class AuthMiddlewareMock(object):

    def process_request(self, req, resp):
        user_groups = ['default']
        req.context['groups'] = user_groups
