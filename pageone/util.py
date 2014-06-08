import requests
from cookielib import CookieJar as cj
from lxml import etree

# helpers for getting static page
def get_request_kwargs(timeout, useragent):
  """
  This Wrapper method exists b/c some values in req_kwargs dict
  are methods which need to be called every time we make a request.
  """
  return {
    'headers' : {'User-Agent': useragent},
    'cookies' : cj(),
    'timeout' : timeout,
    'allow_redirects' : True
  }

def get_html(url, response=None, **kwargs):
  """
  Retrieves the html for either a url or a response object. All html
  extractions MUST come from this method due to some intricies in the
  requests module. To get the encoding, requests only uses the HTTP header
  encoding declaration requests.utils.get_encoding_from_headers() and reverts
  to ISO-8859-1 if it doesn't find one. This results in incorrect character
  encoding in a lot of cases.
  """
  FAIL_ENCODING = 'ISO-8859-1'
  useragent = kwargs.get('useragent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0')
  timeout = kwargs.get('timeout', 10)

  if response is not None:
    
    if response.encoding != FAIL_ENCODING:
      return response.text
    
    return response.content # not unicode, fix later

  try:
    html = None
    response = requests.get(url=url, **get_request_kwargs(timeout, useragent))
    
    if response.encoding != FAIL_ENCODING:
      html = response.text
    
    else:
      html = response.content # not unicode, fix later
    
    if html is None:
      html = u''
    
    return html

  except Exception, e:
    print '%s on %s' % (e, url)
    return u''