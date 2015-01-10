from setuptools import setup, find_packages
import os 
from pip.req import parse_requirements

# hack for workings with pandocs
import codecs 
try: 
  codecs.lookup('mbcs') 
except LookupError: 
  ascii = codecs.lookup('ascii') 
  func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs') 
  codecs.register(func) 

# install readme
readme = os.path.join(os.path.dirname(__file__), 'README.md')

try:
  import pypandoc
  long_description = pypandoc.convert(readme, 'rst', format="md")
except (IOError, ImportError):
  long_description = ""

# parse requirements file
# required = [str(ir.req) for ir in parse_requirements("requirements.txt")]

# setup
setup(
  name='pageone',
  version='0.1.7',
  description='a module for polling urls and stats from homepages',
  long_description = long_description,
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    ],
  keywords='',
  author='Brian Abelson',
  author_email='brian@enigma.io',
  url='http://github.com/newslnyx/pageone',
  license='MIT',
  packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
  namespace_packages=[],
  include_package_data=False,
  zip_safe=False,
  install_requires=[
    "lxml==3.3.5",
    "requests==2.3.0",
    "selenium==2.42.1",
    "siegfried>=0.0.7",
    "wsgiref==0.1.2"
  ],
  tests_require=[]
)