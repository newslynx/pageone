from setuptools import setup, find_packages

# setup
setup(
    name='pageone',
    version='0.2.1',
    description='a module for polling urls and stats from homepages',
    long_description='',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Brian Abelson',
    author_email='brian@newslynx.org',
    url='http://github.com/newslnyx/pageone',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        "selenium==2.47.3"
    ],
    tests_require=['nose']
)
