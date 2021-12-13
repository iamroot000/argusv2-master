from django import forms
from .models import *
from django.conf import settings
import ipaddress, os, json, random



class SSRhomeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SSRhomeForm, self).__init__(*args, **kwargs)
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        config_read = open(config_file, 'r').read()
        condigdata = json.loads(config_read)
        IDC_CHOICES = [('---','---')]
        for i in condigdata["configlist"]["IDC"]:
            IDC_CHOICES.append((i, i))
        self.fields['IDC'].choices = IDC_CHOICES


    IDC = forms.ChoiceField(
        label="IDC", initial='---'
    )
    IP = forms.CharField(max_length=960, widget=forms.Textarea(attrs={'rows':5, 'cols': 16, 'placeholder': "Enter SSR IP"}), label="SSR IP")

    class Meta:
        model = SSRhomehistoryModel
        fields = [
            'IP',
            'IDC'
        ]

    def clean_IDC(self):
        IDC = self.cleaned_data.get("IDC")
        if IDC == '---':
            raise forms.ValidationError("Incorrect IDC!")
        else:
            return IDC

    def clean_IP(self):
        IP = self.cleaned_data.get("IP")
        for IP_list in IP.split('\n'):
            try:
                return str(ipaddress.ip_address(IP_list.strip()))
            except:
                raise forms.ValidationError("Invalid input! It should be IP!")


class SSRinitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SSRinitForm, self).__init__(*args, **kwargs)
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        config_read = open(config_file, 'r').read()
        condigdata = json.loads(config_read)
        IDC_CHOICES = [('---','---')]
        for i in condigdata["configlist"]["IDC"]:
            IDC_CHOICES.append((i, i))
        self.fields['IDC'].choices = IDC_CHOICES

    IP = forms.CharField(max_length=960, widget=forms.Textarea(attrs={'rows':5, 'cols': 16, 'placeholder': "Enter SSR IP"}), label="SSR IP")
    PORT= forms.CharField(max_length=5, initial=22)
    USER = forms.CharField(max_length=15, initial='root')
    PASSWORD = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder':'********','autocomplete': 'off','data-toggle' : 'password'}))
    IDC = forms.ChoiceField(
        label="IDC", initial='---'
    )

    class Meta:
        model = SSRinitModel
        fields = [
            'IP',
            'PORT',
            'USER',
            'PASSWORD',
            'IDC'
        ]

    def clean_USER(self):
        USER = self.cleaned_data.get("USER")
        if USER != 'root':
            raise forms.ValidationError("USER should be root!")
        else:
            return USER

    def clean_IP(self):
        IP = self.cleaned_data.get("IP")
        for IP_list in IP.split('\n'):
            try:
                return str(ipaddress.ip_address(IP_list.strip()))
            except:
                raise forms.ValidationError("Invalid input! It should be IP!")


    def clean_PORT(self):
        PORT = self.cleaned_data.get("PORT")
        try:
            if int(PORT) <= 65535 and int(PORT) > 0:
                return PORT
            else:
                raise forms.ValidationError("Port is out of range.")
        except ValueError:
            raise forms.ValidationError("Invalid Input! It should be PORT!")

    def clean_IDC(self):
        IDC = self.cleaned_data.get("IDC")
        if IDC == '---':
            raise forms.ValidationError("Incorrect IDC!")
        else:
            return IDC



class SSRconfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SSRconfigForm, self).__init__(*args, **kwargs)
        self.fields['PORT'].initial=random.randint(3300, 3400)

    config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
    config_read = open(config_file, 'r').read()
    condigdata = json.loads(config_read)
    IDC_CHOICES = []
    for i in condigdata["configlist"]["IDC"]:
        IDC_CHOICES.append((i, i))

    IP = forms.CharField(max_length=960, widget=forms.Textarea(attrs={'rows':5, 'cols': 16, 'placeholder': "Enter SSR IP"}), label="SSR IP")
    PORT= forms.CharField(max_length=5)



    class Meta:
        model = SSRconfigsummaryModel
        fields = [
            'IP',
            'PORT'
        ]

    def clean_IP(self):
        IP = self.cleaned_data.get("IP")
        for IP_list in IP.split('\n'):
            try:
                return str(ipaddress.ip_address(IP_list.strip()))
            except:
                raise forms.ValidationError("Invalid input! It should be IP!")



    def clean_PORT(self):
        PORT = self.cleaned_data.get("PORT")
        try:
            if int(PORT) <= 65535 and int(PORT) > 0:
                return PORT
            else:
                raise forms.ValidationError("Port is out of range.")
        except ValueError:
            raise forms.ValidationError("Invalid Input! It should be PORT!")


class SSRconfigIDCForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SSRconfigIDCForm, self).__init__(*args, **kwargs)
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        config_read = open(config_file, 'r').read()
        condigdata = json.loads(config_read)
        IDC_CHOICES = [('---','---')]
        for i in condigdata["configlist"]["IDC"]:
            IDC_CHOICES.append((i, i))
        self.fields['IDC'].choices = IDC_CHOICES


    IDC = forms.ChoiceField(
        label="IDC", initial='---'
    )


    class Meta:
        model = SSRconfigsummaryModel
        fields = [
            'IDC'
        ]

    def clean_IDC(self):
        IDC = self.cleaned_data.get("IDC")
        if IDC == '---':
            raise forms.ValidationError("Incorrect IDC!")
        else:
            return IDC

class SSRconfigtextForm(forms.Form):
    def __init__(self, fileconfig=None, fileinitial=None, filechoicesdisabled=False, filelabelname='Config File',*args, **kwargs):
        super(SSRconfigtextForm, self).__init__(*args, **kwargs)
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        config_read = open(config_file, 'r').read()
        condigdata = json.loads(config_read)
        filenames = condigdata["configfile"]
        filename_CHOICES = [('','')]
        for i in filenames.keys():
            filename_CHOICES.append((i, i))

        self.fields['FILE'].initial = fileinitial
        self.fields['FILE'].choices = filename_CHOICES
        self.fields['PREVIOUS'].widget = forms.Textarea(attrs={'id':'filehandler', 'label': filelabelname})
        self.fields['PREVIOUS'].initial = fileconfig
        self.fields['PREVIOUS'].label = filelabelname



    FILE = forms.ChoiceField(
        label="Filename",
        widget = forms.Select(
        attrs={"class": "form-control select2 directory",
               "data-placeholder": "Filename",
               "name": "file",
               "id": "file",
               "style": "width:100%;",
               "onchange": 'textFunction()'})
    )
    PREVIOUS = forms.CharField()

    class Meta:
        model = SSRmasterconfighistoryModel
        fields = [
            'PREVIOUS',
            'FILE'
        ]
