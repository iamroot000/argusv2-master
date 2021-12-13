from django.contrib.auth.mixins import AccessMixin
from django.conf import settings
from django.http import HttpResponse

import time,json, hashlib

class GENERIC_PERMISSION_MIXIN(AccessMixin):
    permission_required=None
    def dispatch(self, request, *args, **kwargs):
        if self.permission_required not in request.session['permissions']:
            self.raise_exception = True
            return self.handle_no_permission()

        return super(GENERIC_PERMISSION_MIXIN, self).dispatch(request, *args, **kwargs)

class DPS_CONTROL_MIXIN(AccessMixin):
    def dispatch(self, request, *args, **kwargs):

        perm = 'can_view_DPS-'+kwargs['business_unit']
        if perm not in request.session['permissions']:
            self.raise_exception = True
            return self.handle_no_permission()

        return super(DPS_CONTROL_MIXIN, self).dispatch(request, *args, **kwargs)

class GroupControlMixin(AccessMixin):
    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.group_required not in request.session['groups']:
            self.raise_exception = True
            return self.handle_no_permission()

        return super(GroupControlMixin, self).dispatch(request, *args, **kwargs)


class omonlyMixin(AccessMixin):
    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if not settings.DEBUG:
            if not 'om' in request.session['attr']['dept']:
                self.raise_exception=True
                return self.handle_no_permission()

        return super(omonlyMixin, self).dispatch(request, *args, **kwargs)


class timeTokenAccessMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):

        body = json.loads(request.body)

        Token_STR = settings.API_TOKEN
        timeStamp = time.time()
        req_token = body['token']
        req_timestamp = body['timestamp']

        if not 10 > (int(timeStamp) - int(req_timestamp)) > -10:
            return HttpResponse(json.dumps({'status': 403, 'msg': 'Authentication Failed: Token Expired'}), content_type='application/json')

        md5_handler = hashlib.md5(str(Token_STR + req_timestamp).encode('utf-8'))

        if req_token == md5_handler.hexdigest():
            return super(timeTokenAccessMixin, self).dispatch(request, *args, **kwargs)
        return HttpResponse(json.dumps({'status': 403, 'msg': 'Authentication Failed: Incorrect token'}), content_type='application/json')


class MultipleBUMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        perm = 'can_view_eye-'+kwargs['business_unit']
        if perm not in request.session['permissions']:
            self.raise_exception = True
            return self.handle_no_permission()
        return super(MultipleBUMixin, self).dispatch(request, *args, **kwargs)
