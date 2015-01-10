from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
  NoSuchElementException, StaleElementReferenceException, TimeoutException
  )
from datetime import datetime
import socket
from siegfried import (
  is_article_url, prepare_url, urls_from_html, get_simple_domain
  )

from util import get_html

class PageoneInitError(Exception):
  pass

class PageOne:
  def __init__(self, **kwargs):
    if 'url' not in kwargs:
      raise PageoneInitError(
        'PageOne requires a '
        'url to run its methods.'
        )

    self.url = kwargs.get('url')
    self.max_tries = kwargs.get('max_tries', 10)
    self.domain = get_simple_domain(self.url)

  def readystate_complete(self):
    # AFAICT Selenium offers no better way to wait for the document to be loaded,
    # if one is in ignorance of its contents.
    return self.browser.execute_script("return document.readyState") == "complete"

  def get_homepage_safely(self):
    tries = 0
    try:
      self.browser.get(self.url)
      WebDriverWait(self.browser, 30).until(self.readystate_complete)
    
    except TimeoutException:
      self.browser.execute_script("window.stop();")

    except socket.timeout:
      while 1:

        try:
          self.browser.get(self.url)
          WebDriverWait(self.browser, 5).until(readystate_complete)
    
        except TimeoutException:
          self.browser.execute_script("window.stop();")

        except:
          tries += 1
          
          if tries == self.max_tries:
            break
        
        else:
          break

    except Exception as e:
      pass

  def get_url(self, link):
    url = link.get_attribute("href")
   
    if url:
      return prepare_url(url, source_url = self.url)
   
    else:
      return ''

  def get_img_data(self, link):
    try:
      img = link.find_element_by_tag_name("img")
    
    except NoSuchElementException:
      img = None
    
    if img is not None:
      w = int(img.get_attribute("width"))
      h = int(img.get_attribute("height"))
      
      return {
        'has_img': 1,
        'img_width': w,
        'img_height': h,
        'img_area': w * h,
        'img_src': img.get_attribute("src")
      }
    
    else:
      return {
        'has_img': 0,
        'img_width': None,
        'img_height': None,
        'img_area': None,
        'img_src': None
      }

  def get_font_size(self, link):
    return int(link.value_of_css_property('font-size')[:-2])

  def get_link_coords(self, link):
    x = int(link.location['x'])
    y = int(link.location['y'])
    return x, y

  def bucket_coord(self, c):
    """
    Simply divide the coordinate by the number of pixels 
    per bucket.
    """
    return int(c / self.bucket_pixels) + 1

  def get_bucket_data(self, x, y):
    """
    Assign coordinates into buckets, moving from top left
    to bottom right.
    """
    if  x == 0 and y == 0:
      return {
        'x_bucket': None,
        'y_bucket': None,
        'bucket': None
      }

    else:
      x_b = self.bucket_coord(x)
      y_b = self.bucket_coord(y)
      
      return {
        'x_bucket': x_b,
        'y_bucket': y_b,
        'bucket': (x_b + y_b) - 1
      }

  def valid_link(self, link):
    """
    Validate a link
    """

    # only get visible links
    if self.visible_only:
      
      try:
      
        if not link.is_displayed():
          return False
      
      except (NoSuchElementException, StaleElementReferenceException):
        return False

    # only get valid links
    url = self.get_url(link)
    
    if is_article_url(url, pattern = self.pattern):
    
      if not self.incl_external and self.domain not in url:
        return False
    
      else:
        return True

    # default to invalid
    return False


  def parse_link(self, link):
    
    url = self.get_url(link)          

    # get coordinates
    x, y = self.get_link_coords(link) 

    # bucket coordinates
    bucket_dict = self.get_bucket_data(x, y)

    # get image
    img_dict = self.get_img_data(link)

    link_dict = {
      'homepage' : self.url,
      'datetime': datetime.utcnow(),
      'headline' :  link.text.strip(),
      'url': url,
      'font_size' : self.get_font_size(link),
      'x' : x,
      'y' : y
    }

    data = dict(
      link_dict.items() + 
      img_dict.items() + 
      bucket_dict.items()
      )          

    # return data
    return data

  def link_stats(self, **kwargs):
    
    # get kwargs
    self.bucket_pixels = kwargs.get('bucket_pixels', 200)
    self.phantom_path = kwargs.get('phantom_path', '/usr/local/bin/phantomjs')
    self.visible_only = kwargs.get('visible_only', True)
    self.pattern = kwargs.get('pattern', None)
    self.incl_external = kwargs.get('incl_external', False)
    
    # open browser
    self.browser  = webdriver.PhantomJS(self.phantom_path)
    
    # open homepage
    self.get_homepage_safely()
    links = self.browser.find_elements_by_tag_name('a')

    # get valid link stats
    for link in links:
      
      if self.valid_link(link):
        yield self.parse_link(link)

    # quit the browser at the end
    self.browser.quit()

  def articles(self, pattern = None, incl_external=False):
    """
    Get all the article links on the homepage.
    """

    html = get_html(self.url)
    urls = urls_from_html(html, dedupe=True)

    for u in urls:

      if is_article_url(u, pattern = pattern):

        if not incl_external and self.domain in u:
          yield prepare_url(u, source_url = self.url)

        else:
          yield prepare_url(u, source_url = self.url)

