rpSelenzyme's documentation
===========================

Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
############

.. _rpSBML: https://github.com/Galaxy-SynBioCAD/rpBase
.. _rpBase: https://github.com/Galaxy-SynBioCAD/rpBase
.. _ReactionRules: https://retrorules.org/doc
.. _Selenzyme: https://github.com/pablocarb/selenzyme_tool

Welcome to the documentation for rpSelenzyme. This project extends the Selenzyme_ project from Pablo Carbonel to be used by rpSBML_ files, and parse the ReactionRules_ within the files. 

Usage
#####

First build the rpBase_ docker before building the local docker:

.. code-block:: bash

   docker build -t brsynth/rpselenzyme-standalone:v2 -f Dockerfile .

To call the docker locally you can use the following command:

.. code-block:: bash

   python run.py -input /path/to/file -input_format tar -taxonomy_input 83333 -taxonomy_format string -output /path/to/output

API
###

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. currentmodule:: rpToolServe

.. autoclass:: runSelenzyme_hdd
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: rpTool

.. autoclass:: singleReactionRule
    :show-inheritance:
    :members:
    :inherited-members:

.. autoclass:: singleSBML
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: run

.. autoclass:: main
    :show-inheritance:
    :members:
    :inherited-members:
