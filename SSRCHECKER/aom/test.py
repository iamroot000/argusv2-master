from subprocess import call
import requests

r = requests.get('http://ptgmr.gameapi.info').status_code
print(r)

