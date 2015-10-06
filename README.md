[![travis-img](https://travis-ci.org/newslynx/pageone.svg)](https://travis-ci.org/newslynx/pageone)
pageone
======
_a module for polling urls and stats from homepages_

## Install
```bash
pip install pageone
```

## Test
Requires `nose`

```bash
nosetests
```

## Usage
`pageone` does two things: extract article urls from a site's homepage and also uses `selenium` and `phantomjs` to find the relative positions of these urls.

`pageone` provides a single interface:

```python
import pageone

for link in pageone.get('http://www.propublica.org/', pattern='.*articles.*'):
    print link
```
Here, `pattern` represents `regex` used to identify which urls are artilces. If `newslynx` is installed and `pattern` is not provided, it will default to using [`newslynx.lib.url.is_article`](https://github.com/newslynx/newslynx-core/blob/master/newslynx/lib/url.py#L342), which uses a series of heuristics to determine whether a url is an article.

All methods will return a list of dictionaries that look like this:

```python
{
 'bucket': 8,
 'bucket_size': 200,
 'datetime': datetime.datetime(2015, 10, 6, 20, 21, 22, 422478),
 'domain': 'www.propublica.org',
 'font_size': 14,
 'n_links': 1,
 'page': 'http://www.propublica.org/',
 'text': u'The Stories of Everyday Lives, Hidden in Reams of Data',
 'url': u'https://www.propublica.org/nerds/item/the-stories-of-everyday-lives-hidden-in-reams-of-data/',
 'visible': True,
 'x': 61,
 'x_bucket': 1,
 'y': 1578,
 'y_bucket': 8
}
```

Here `bucket` variables represent where a link falls in 200x200 pixel grid.  For `x_bucket` this number moves from left-to-right. For `y_bucket`, it moves top-to-bottom.  `bucket` moves from top-left to bottom right.  You can customize the size of this grid by passing in `bucket_pixels` to `get`, eg:

```python
import pageone

for link in pageone.get('http://www.propublica.org/', bucket_pixels = 100):
    print link
```

## PhantomJS
`pageone` requires [phantomjs](http://phantomjs.org/) to run `pageone.get()`.  `pageone` defaults to looking for `phantomjs` in `/usr/bin/local/phantomjs`, but if you want to specify another path, pass in `phantom_path` to `pageone.get`:

```python
import pageone

for link in pageone.get('http://www.propublica.org/', pattern='.*articles.*', phantom_path="/usr/bin/phantomjs"):
    print link
```