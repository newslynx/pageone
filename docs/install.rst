Installation Guide
==================

To install ``pageone``, run the following commands in your terminal. It is **highly** reccomended that you initialize a virtual environment with ``virtualenvwrapper``:

.. code-block:: bash

   $ mkvirtualenv pageone
   $ git clone https://github.com/newslnyx/pageone.git
   $ cd pageone
   $ pip install -r requirements.txt
   $ pip install .

Tests can be run with ``nose`` in the projects root directory:

.. code-block:: bash

   $ nosetests


