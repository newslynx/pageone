import re
import os
from urlparse import (
    urlparse, urljoin, urlsplit, urlunsplit
)
from traceback import format_exc
from datetime import datetime
import socket
import time
from collections import defaultdict
from operator import itemgetter

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, StaleElementReferenceException, TimeoutException
)

from .exc import PageOneError

KEEP_PARAMS = ('id', 'p', 'v')

RE_TYPE = type(re.compile(r''))


class PageOne:

    def __init__(self, **kw):
        if 'page' not in kw:
            raise PageOneError(
                'PageOne requires a '
                'url to run its methods.'
            )

        self.page = kw.get('page')
        self.max_tries = kw.get('max_tries', 3)
        self.wait = kw.get('wait', 2)
        self.backoff = kw.get('backoff', 1.5)
        self.timeout = kw.get('timeout', 30)
        self.domain = urlparse(self.page).netloc

    # CORE Method

    def links(self, **kw):
        """
        Get stats about article links.
        """
        # get kw
        self._bucket_size = kw.get('bucket_size', 200)
        self._visible_only = kw.get('visible_only', True)
        self._incl_external = kw.get('incl_external', False)
        self._uniq = kw.get('uniq', True)

        # open browser
        self._init_browser(**kw)

        # open homepage
        err = self._get_page()
        if err:
            # quit the browser at the end
            self._stop_browser()
            raise PageOneError('Could not open {}'.format(self.page))

        # parse all the links
        try:
            if not self._uniq:
                for link in self._get_links(**kw):
                    yield link
            else:
                for link in self._agg_links(**kw):
                    yield link
        except Exception as e:
            # quit the browser at the end
            self._stop_browser()
            raise PageOneError(format_exc())
        self._stop_browser()

    # User-configurable methods.

    def now(self, **kw):
        """
        Set the current datetime.
        """
        return datetime.utcnow()

    def is_article_url(self, u, **kw):
        """
        Overridable function for testing whether an article
        leads to a url.
        """
        print u
        if not u:
            return False
        p = kw.get('pattern', None)
        if not p:
            raise PageOneError(
                'A "pattern" is required to identify '
                'which link urls point to articles.')
        if not isinstance(p, RE_TYPE):
            p = re.compile(p)
        return p.search(u) is not None

    def prepare_url(self, u, **kw):
        """
        Overridable function for normalizing a url.
        """
        keep_params = kw.get('keep_url_params', KEEP_PARAMS)
        frags = kw.get('keep_frags', False)
        if not u:
            return None
        if u.startswith('/'):
            u = urljoin(self.page, u)
        parsed = urlsplit(u)
        filtered_query = '&'.join(
            qry_item for qry_item in parsed.query.split('&')
            if qry_item.startswith(keep_params)
        )
        if frags:
            frag = parsed[4:]
        else:
            frag = ('',)
        return urlunsplit(parsed[:3] + (filtered_query,) + frag)

    # INTERNAL - Brower Function.

    def _init_browser(self, **kw):
        """
        Start Phantom.
        """
        # open browser
        default = os.getenv('PAGEONE_PHANTOM_PATH', "/usr/local/bin/phantomjs")
        self.b = webdriver.PhantomJS(
            kw.get('phantom_path', default)
        )

    def _stop_browser(self):
        self.b.quit()
        try:
            self.b.close()
        except:
            pass

    def _ready(self, browser):
        """
        Check if a page is ready.
        """
        # AFAICT Selenium offers no better way to wait
        # for the document to be loaded,
        # if one is in ignorance of its contents.
        return browser\
            .execute_script("return document.readyState") == "complete"

    def _try(self):
        """
        try to get the page once.
        """
        try:
            self.b.get(self.page)
            WebDriverWait(self.b, self.timeout).until(self._ready)

        except TimeoutException:
            self.b.execute_script("window.stop();")
            raise Exception('Timeout.')

        except socket.timeout as e:
            raise Exception(e.message)

    def _get_page(self):
        """
        Get the homepage.
        """
        tries = 0
        err = True
        while 1:
            try:
                self._try()
                err = False
            except Exception as e:
                raise e
                tries += 1
                if tries == self.max_tries:
                    break
            else:
                break
        return err

    def _is_visible(self, link):
        """
        check if a link is visible.
        """
        try:
            if not link.is_displayed():
                return False
        except (NoSuchElementException, StaleElementReferenceException):
            return False
        x, y = self._get_coords(link)
        return (x != 0 and y != 0)

    def _get_href(self, link, **kw):
        """
        get the href attribute of a link.
        """
        u = link.get_attribute("href")
        if u:
            return self.prepare_url(u, source=u)
        return None

    # def _get_img(self, link, **kw):
    #     """
    #     get images assoicated with this link.
    #     """
    #     try:
    #         img = link.find_element_by_tag_name("img")

    #     except NoSuchElementException:
    #         img = None

    #     if (img is not None and kw.get('visible')):
    #         w = int(img.get_attribute("width"))
    #         h = int(img.get_attribute("height"))
    #         return {
    #             'has_img': True,
    #             'img_width': w,
    #             'img_height': h,
    #             'img_area': w * h,
    #             'img_src': img.get_attribute("src")
    #         }

    #     return {
    #         'has_img': False,
    #         'img_width': None,
    #         'img_height': None,
    #         'img_area': None,
    #         'img_src': None
    #     }

    def _get_font_size(self, link, **kw):
        """
        Get the font size of a link.
        """
        return int(link.value_of_css_property('font-size')[:-2])

    def _get_coords(self, link, **kw):
        """
        Get the coords of a link.
        """
        x = int(link.location['x'])
        y = int(link.location['y'])
        return x, y

    def _bucket_coord(self, c):
        """
        Simply divide the coordinate by the number of pixels
        per bucket.
        """
        return int(c / self._bucket_size) + 1

    def _get_position(self, link, **kw):
        """
        Assign coordinates into buckets, moving from top left
        to bottom right.
        """
        # get coordinates
        d = {}
        d['x'], d['y'] = self._get_coords(link, **kw)
        if not kw.get('visible'):
            d.update({
                'x_bucket': None,
                'y_bucket': None,
                'bucket': None,
                'bucket_size': self._bucket_size
            })
        else:
            x_b = self._bucket_coord(d['x'])
            y_b = self._bucket_coord(d['y'])
            d.update({
                'x_bucket': x_b,
                'y_bucket': y_b,
                'bucket': (x_b + y_b) - 1,
                'bucket_size': self._bucket_size
            })
        return d

    def _valid_link(self, link, **kw):
        """
        Validate a link
        """
        # only get valid links
        u = self._get_href(link)
        if not u:
            return False

        if self.is_article_url(u, pattern=kw.get('pattern')):
            if not self._incl_external and self.domain not in u:
                return False
            else:
                return True

        # default to invalid
        return False

    def _parse_link(self, link, **kw):

        # format output
        output = {
            'page': self.page,
            'domain': self.domain,
            'datetime': self.now(),
            'visible': kw.get('visible', True),
            'text':  link.text.strip(),
            'url': self.prepare_url(self._get_href(link)),
            'font_size': self._get_font_size(link, **kw),
        }

        # add in other dicts
        return dict(
            output.items() +
            self._get_position(link, **kw).items()
        )

    def _get_links(self, **kw):
        """
        get all the links.
        """
        for link in self.b.find_elements_by_tag_name('a'):
            kw['visible'] = self._is_visible(link)
            # ignore hidden links
            if (self._visible_only and not kw['visible']):
                continue

            # check if a link is valid
            if self._valid_link(link, **kw):
                # parse
                yield self._parse_link(link, **kw)

    def _agg_links(self, **kw):
        """
        Return a list of unique links.
        """
        # first build up a group of all unique urls.
        groups = defaultdict(list)
        lookup = defaultdict(list)
        for i, link in enumerate(self._get_links(**kw)):
            # keep track of ids. will be useful when reconciling.
            # build up list of ids
            link['id'] = i
            groups[link['url']].append((i, link))
            lookup[i] = link

        # summarize
        for group in groups.values():

            #  init
            n = len(group)
            ids = [id for id, g in group]
            group = [g for id, g in group]

            # default to highest ranked link.
            group = sorted(group, key=itemgetter("bucket"))
            agg = group[0]
            agg['n_links'] = n
            #
            if n != 1:
                # choose the best candidate by a combination filter of
                # visibility + url + img + headline + bucket

                # top position by bucket
                bucket_ids = list(
                    l['id']
                    for l in sorted(group, key=itemgetter("bucket"))
                    if l.get('bucket')
                )

                # top headline by length
                text_ids = list(
                    l['id']
                    for l in sorted(group, key=lambda g: len(g['text']), reverse=True)
                    if l['text']
                )

                # visible ids
                visible_ids = list(
                    l['id'] for l in group if l['visible']
                )

                # select the best candidate.
                for id in ids:

                    if all([id in l for l in [bucket_ids, text_ids, visible_ids]]):
                        agg.update(lookup[id])
                        break

                    elif all([id in l for l in [bucket_ids, visible_ids]]):
                        agg.update(lookup[id])
                        break

                    elif all([id in l for l in [bucket_ids]]):
                        agg.update(lookup[id])
                        break
            agg.pop('id')
            yield agg
