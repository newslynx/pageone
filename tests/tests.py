import unittest
import os
import pageone

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.join(TEST_DIR, 'fixtures')

p = r'(.*projects\.propublica\.org/.*)|(.*/article/.*)'


for link in pageone.get('https://www.propublica.org/', pattern=p):
    print link


class Tests(unittest.TestCase):

    def test_link_stats(self):
        """
        TK: better tests, I'm just checking it runs for now:
        """
        for link in pageone.get('https//www.propublica.org/', uniq=True):
            print link
