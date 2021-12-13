from django import forms
from .models import *
from django.conf import settings
import requests


class JenkinsapiForms(forms.ModelForm):
    URL = forms.CharField(max_length=960, label="Jenkins API")

    class Meta:
        model = JenkinsModel
        fields = [
            'URL'
        ]


    def clean_URL(self):
        URL = self.cleaned_data.get("URL")
        url_list = URL.split('/')
        for j_list in url_list:
            if len(j_list) == 0:
                url_list.remove(j_list)
        if len(url_list) != 5:
            raise forms.ValidationError("Invalid input! It should be http://<jenkins_url>/<jobdir>/<jobname>/<jobnumber>/")
        if url_list[-2].split('_')[-1] == 'TEST':
            raise forms.ValidationError("Jobname should be REAL")
        return URL
