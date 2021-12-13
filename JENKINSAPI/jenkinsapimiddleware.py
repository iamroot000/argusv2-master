from django.http import Http404, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseForbidden
from .urls import *
from django.conf.urls import url
from JENKINSAPI.views import *



class JenkinsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if "jenkinsapi" in request.path:
            urllenall = request.path.split('/')
            urllen = []
            for i in urllenall:
                if len(i) != 0:
                    urllen.append(i)
            print(len(urllen))
            if len(urllen) == 5:
                return redirect('google.com')
