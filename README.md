![travis-img](https://travis-ci.org/newslnyx/pageone.svg)
pageone
======
_a module for polling urls and stats from homepages_

## Install
```bash
mkvirtualenv pageone
git clone https://github.com/newslnyx/pageone.git
cd pageone
pip install -r requirements.txt
pip install .
```

## Test
Requires `nose`

```
nosetests
```

## Usage
`pageone` does two things: extract article urls from a site's homepage and also uses `selenium` and `phantomjs` to find the relative positions of these urls.

To get stats about the positions of links, use `link_stats`:

```python
from pageone import PageOne

p = PageOne(url='http://www.propublica.org/')

# get stats about links positions
for link in p.link_stats():
    print link
```

This will return a list of dictionaries that look like this:

```python
{'bucket': 4,
 'datetime': datetime.datetime(2014, 6, 7, 16, 6, 3, 533818),
 'font_size': 13,
 'has_img': 1,
 'headline': u'',
 'homepage': 'http://www.propublica.org/',
 'img_area': 3969,
 'img_height': 63,
 'img_src': u'http://www.propublica.org/images/ngen/gypsy_image_medium/mpmh_victory_drive_140x140_130514_1.jpg',
 'img_width': 63,
 'url': u'http://www.propublica.org/article/protect-service-members-defense-department-plans-broad-ban-high-cost-loans',
 'x': 61,
 'x_bucket': 1,
 'y': 730,
 'y_bucket': 4}
```

To get simply get all of the article urls on a homepage, use `articles`:

```python
from pageone import PageOne
p = PageOne(url='http://www.propublica.org/')

for article in p.articles():
  print article
```

If you want to get article urls from other sites, use `incl_external`:

```python
from pageone import PageOne
p = PageOne(url='http://www.propublica.org/')

for article in p.articles(incl_external=True):
  print article
```