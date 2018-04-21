macroecon
=========

.. image:: https://img.shields.io/pypi/v/macroecon.svg
    :target: https://pypi.python.org/pypi/macroecon
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/pfcor/macroecon.png
   :target: https://travis-ci.org/pfcor/macroecon
   :alt: Latest Travis CI build status

Interface with macroeconomic data sources from Brasil.

Still in early development. Many changes will come to the API.

Implemented data sources:
- [Ipea](http://www.ipeadata.com.br) 

Usage
-----

>>> from macroecon import ipeadata
>>> series = ipeadata.get_series_data(37667)
>>> series.head()
        date   37667
0 1940-07-01  816.27
1 1940-08-01  813.99
2 1940-09-01  813.26
3 1940-10-01  800.53
4 1940-11-01  782.53


Installation
------------

pip install macroecon

Requirements
^^^^^^^^^^^^
pandas
requests
bs4

Compatibility
-------------
Python 3.6

Authors
-------

`macroecon` was written by `Pedro Correia <pedrocorreia.rs@gmail.com>`_.
