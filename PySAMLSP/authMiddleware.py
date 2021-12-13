from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


#ADD EXEPMTED URLS HERE
LOGIN_EXEMPT_URLS = (
        '/acs',
        '/auth',
    )


class authMiddleware(MiddlewareMixin):

    def process_request(self, request):
        #print request.session['auth']['user']
        try:

            request.session['auth']['user']

        except:
            path = request.path_info
            if path not in LOGIN_EXEMPT_URLS:
                return redirect('/auth')
