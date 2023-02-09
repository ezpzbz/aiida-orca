===============
Developer guide
===============


Installing
+++++++++++++++++
Install `aiida-orca` in development mode by::

    git clone https://github.com/pzarabadip/aiida-orca
    cd aiida-orca
    pip install -e .[pre-commit,test]
    pre-commit install

Having `pre-commit` hooks installed, flags necessary formatting and linting
changes at the commit stage.

Running the tests
+++++++++++++++++

Please fork the repo and open a PR with your changes when tests are passing locally via invoking::

    pytest tests

Moreover, to run the end-to-end tests, that require the `ORCA`` package installed, run::
    
    pytest examples/

or using multiple cores with OpenMPI parallelization::

    pytest --nproc 2 examples/


Building the documentation
++++++++++++++++++++++++++

 #. Install the ``docs`` extra::

        pip install -e .[docs]

 #. Edit the individual documentation pages::

        docs/source/index.rst
        docs/source/developer_guide/index.rst
        docs/source/user_guide/index.rst
        docs/source/user_guide/get_started.rst
        docs/source/user_guide/tutorial.rst

 #. Use `Sphinx`_ to generate the html documentation::

        cd docs
        make

Check the result by opening ``build/html/index.html`` in your browser.

.. _ReadTheDocs: https://readthedocs.org/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
