"""
WebApplication stepper (test harness)
"""


import re
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.cookiejar

# Default stepper configuration for 
# webapp.py running on localhost at port 8080

site = 'http://localhost:8000/'
path = ''
webAppPage = 'webapp.py'
logoutPage = 'logout.py'

webAppUrl = site + path + webAppPage
logoutUrl = site + path + logoutPage

# user in model : user in implementation

users = { "OleBrumm":"user1", "VinniPuhh":"user2" }
passwords = { "user1":"123", "user2":"234" }
wrongPassword = "000"

debuglevel = 0     # for debug_handler 1: print HTTP headers, 0: don't print
show_page = False

# Optionally rebind configuration. If no Config module found, retain defaults.

try:
  from Config import *
except ImportError:
  pass 

print(f'webAppUrl: {webAppUrl}')

# handlers that are the same for all users

redirect_handler= urllib.request.HTTPRedirectHandler()
debug_handler = urllib.request.HTTPHandler(debuglevel=debuglevel)

# handlers that are different for each user are part of the session state

class Session(object):
  """
  One user's session state: cookies and handlers
  """
  def __init__(self):
    self.cookies = http.cookiejar.CookieJar()
    self.cookie_handler = urllib.request.HTTPCookieProcessor(self.cookies)
    self.opener = urllib.request.build_opener(self.cookie_handler,
                                       redirect_handler,debug_handler)

session = {}

# helpers, determine test results by scraping the page

# like in NModel WebApplication WebTestHelper
def loginFailed(page):
  return (page.decode().find('Incorrect login') > -1)

# not in NModel WebApplication, it has no positive check for login success
def loginSuccess(page):
  return (page.decode().find('DoStuff') > -1)

# similar to NModel WebApplication WebTestHelper
intPattern = re.compile(r'Number: (\d+)')

def intContents(page):
  if m := intPattern.search(page):
    return int(m.group(1))

# stepper core

def TestAction(aname, args, modelResult):
  """
  To indicate success, no return statement (or return None)
  To indicate failure, return string that explains failure
  Test runner also treats unhandled exceptions as failures
  """

  global session

  if aname == 'Initialize':
    session = {}

  elif aname == 'Login':
    user = users[args[0]]
    if user not in session:
      session[user] = Session()
    password = passwords[user] if args[1] == 'Correct' else wrongPassword
    postArgs = urllib.parse.urlencode({'username':user, 'password':password})
    # GET login page
    page = session[user].opener.open(webAppUrl).read()
    if show_page:
      print(page)
    # POST username, password
    page = session[user].opener.open(webAppUrl, postArgs.encode()).read()
    if show_page:
      print(page)
    result = 'Failure' if loginFailed(page) else 'Success'
    if result != modelResult:
      return f'received Login {result}, expected {modelResult}'

  elif aname == 'Logout':
    user = users[args[0]]
    page = session[user].opener.open(logoutUrl).read()
    del session[user] # clear out cookie/session ID
    if show_page:
      print(page)

  elif aname == 'UpdateInt':
    user = users[args[0]]
    numArg = urllib.parse.urlencode({'num':args[1]})
    page = (session[user].opener.open(
        f"{webAppUrl}?{numArg.encode()}").read().decode())
    if show_page:
      print(page)

  elif aname == 'ReadInt':
    user = users[args[0]]
    page = session[user].opener.open(webAppUrl).read().decode()
    if show_page:
      print(page)
    numInPage = intContents(page)
    if numInPage != modelResult:  # check conformance
      return f'found {numInPage} in page, expected {modelResult}'
    else:
      return None
  else:
    raise NotImplementedError(f'action {aname} not handled by stepper')


def Reset():
  global session
  session.clear()
