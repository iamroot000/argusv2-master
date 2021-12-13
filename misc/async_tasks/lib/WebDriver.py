from pyvirtualdisplay import Display
from selenium import webdriver

from base64 import b64encode
import socket
import os

socket.setdefaulttimeout(500)

STATIC_FILE_PATH = os.getcwd() +'/res/screenshots/'
class WebDriver(object):
    def __init__(self):
        self.browser_count = 0
        self.MAX_browser_count = 10
        self.window_wid = 1366
        self.window_len = 768

        self.MAIN_DISPLAY = Display(visible=0, size=(self.window_wid, self.window_len))
        self.MAIN_DISPLAY.start()
        print 'MAIN_DISPLAY STARTED PID: {0}'.format(self.MAIN_DISPLAY.pid)

    def __del__(self):
        self.MAIN_DISPLAY.stop()

    def get_screenshot(self,URL,name=None,mobile=False):
        print 'http://' + URL +' - '+name + ' - START'
        __browser = webdriver.Firefox(timeout=100)
        __browser.set_window_size(self.window_wid,self.window_len)
        __browser.set_page_load_timeout(500)

        __browser.get('http://'+URL)
        fname = STATIC_FILE_PATH
        rpath = 'static/screenshots/' + name + '.png'
        if name is not None:
            fname = fname+name+'.png'
        else:
            fname = fname + b64encode(URL) + '.png'
            rpath = 'static/screenshots/' + b64encode(URL) + '.png'

        __browser.save_screenshot(fname)
        print 'http://'+URL+ ' - '+fname+' - SAVED'



        __browser.quit()

        return rpath


