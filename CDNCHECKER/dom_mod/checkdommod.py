import os

def check():
    process = os.popen("ps ax")
    for i in process.read().split("\n"):
        if "domainchecker.py" not in i:
            os.system("python3 domainchecker.py")
            return "Domainchecker restarted."
        else:
            return "Domainchecker is running"
