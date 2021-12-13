from django.http import Http404, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseForbidden
from .urls import *


class SSRMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        ssr_manager_group = ["PROXYCONTROLLER-GROUP", "PROXYCONTROLLER-GROUP".lower(), "OM-GROUP", "OM-GROUP".lower()]
        ssr_file_group = ["OM-GROUP", "OM-GROUP".lower()]
        group = []
        for i in request.user.groups.all():
            group.append(i.name)

        if "/vpn-manager/file-configuration/" in request.path:
            if any(elem in ssr_file_group  for elem in group) is False and request.user.is_superuser is False:
                raise Http404()

        elif 'vpn-manager' in request.path:
            if any(elem in ssr_manager_group  for elem in group) is False and request.user.is_superuser is False:
                raise Http404()
