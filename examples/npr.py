from pageone import PageOne 

p = PageOne(url='http://npr.org')

for article in p.link_stats():
	print article