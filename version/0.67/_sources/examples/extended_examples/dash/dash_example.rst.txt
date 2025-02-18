.. _dash_example:

Use Dash to build a PyMAPDL web app
===================================

This example shows how to use Dash to build a web app for a simple FEA problem.

Dash is a low-code framework for building data apps which are rendered in a web browser. 
For Dash documentation, refer to: https://dash.plotly.com/


Required modules
----------------

For this example, install modules as needed:

* `dash <dash_>`_
* `dash_bootstrap_components <dash_bootstrap_components_>`_
* `plotly.express <plotly_express_>`_
* `webbrowser <webbrowser_library_>`_
* `pandas <pandas_org_>`_


Structure
---------

* Description page. 
  Read the problem statement 
* Simulation Page. 
  Allow to change the input values, solve the problem and plot the results.
* Data Page. 
	Allow to plot data in a table and graph


Usage
-----

Download the zip file from the link below and unzip it to a folder.
Run the Python file ``BimetallicStrip.py`` which launches the app in your default browser.

:download:`dash extra files <dash-vm35.zip>`
