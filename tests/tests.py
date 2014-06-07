import unittest
import os
from pageone import PageOne

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.join(TEST_DIR, 'fixtures')

class Tests(unittest.TestCase):
  
  def test_link_stats(self):
    """
    TK: better tests, I'm just checking it runs for now:
    """
    p = PageOne(url='http://www.propublica.org/')
    link_data = [l for l in p.link_stats()]
    assert len(link_data) > 5

  def test_articles(self):
    p = PageOne(url='http://www.propublica.org/')
    articles = [a for a in p.articles()]
    assert len(articles) > 10