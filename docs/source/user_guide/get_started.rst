===============
Getting started
===============

Installation
++++++++++++

Use the following commands to install the plugin::

    In order to install the latest release, you may do:

    pip install aiida-orca

    Developers can clone it locally by:

    git clone https://github.com/pzarabadip/aiida-orca .
    cd aiida-orca
    pip install -e .
    #pip install -e .[pre-commit,testing] # install extras for more features


Available calculations
++++++++++++++++++++++

.. aiida-calcjob:: OrcaCalculation
    :module: aiida_orca.calculations

.. aiida-calcjob:: OrcaAsaCalculation
    :module: aiida_orca.calculations
