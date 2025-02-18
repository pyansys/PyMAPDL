.. _ref_unit_testing_contributing:

Unit Testing
============

Unit tests validate the software by testing that the logic
implemented inside a certain method, class, or module is
working as expected. They should be as atomic and 
independent as possible.

Unit testing is highly important. The tests check that code
changes are consistent with other parts of the code
and verify that these changes are implemented properly.

Unit tests are in the `tests <pymapdl_tests_>`_ directory in this repository,
along with integration tests. The difference between
a unit test and an integration test is that the latter
tests several units of the code to ensure that they all work together.

To verify that all code is properly tested, you must ensure that every piece
of code is used (covered) in at least one unit test. In this repository, the
`Codecov <codecov_>`_ tool generates a coverage report of the
committed code. It details how merging a pull request would impact coverage. It
is one of the checks that must run successfully to merge code changes.


.. figure:: ../images/codecov_increase.png
    :width: 400pt


Coverage example
----------------

To show how the coverage works, assume that you have
this library:

**My awesome library**


.. code:: python

    def get_report_colors(theme):
        if theme == "weather":
            colors = ["blue", "lightblue", "grey"]
        elif theme == "traffic":
            colors = ["red", "orange", "yellow"]
        else:
            colors = ["red", "blue", "green"]

        return colors


**Tests**

You can opt to run the tests with this configuration:

.. code:: python

   def test_get_report_colors():
       assert get_report_colors("weather") == ["blue", "lightblue", "grey"]
       assert get_report_colors("traffic") == ["red", "orange", "yellow"]
       assert get_report_colors("other") == ["red", "blue", "green"]


Or, if a method is a bit more complex, you can split the case in different tests:

.. code:: python

    def test_get_report_colors_weather():
        assert get_report_colors("weather") == ["blue", "lightblue", "grey"]


    def test_get_report_colors_traffic():
        assert get_report_colors("traffic") == ["red", "orange", "yellow"]


    def test_get_report_colors_other():
        assert get_report_colors("other") == ["red", "blue", "green"]


While the code coverage in either case is 100% for the function, the second case is
more useful for debugging the function.


Continuous Integration and Continuous Deployment (CI/CD) approach
-----------------------------------------------------------------

Unit tests and integration tests are part of Continuous Integration (CI). 
The automation of testing, monitoring, and deployment of newly added
code allows Continuous Deployment (CD) throughout the application
lifecycle, providing a comprehensive CI/CD approach.

.. figure:: ../images/cicd.jpg
    :width: 300pt

Creation of a unit test
-----------------------

In the PyMAPDL repository, `pytest <pytest_>`_ is used to run tests. 

The name of a ``pytest`` file must be in the form ``test_XXX.py``, where ``XXX``
is either the function, method, or class that you are testing or some other explicative
name. In the command line, the ``-k`` argument can be used to filter the tests to run.
For more information, see `pytest usage <pytest_usage_>`_.

Here are some guidelines for creating good unit tests: 

- Assign long and descriptive names to tests.
- Use the `Codecov <codecov_>`_ tool to ensure all implemented code is tested.
- Check that tests return the same results each time. 
- Verify that tests are independent.
- Write tests that verify only one part of the code at a time.
- Make tests as short and fast as possible.

`What makes a good unit test <article_good_unit_test_>`_ 
is an exhaustive list of tips for creating good unit tests.

Most PyMAPDL tests require a connection to a running instance of
MAPDL, which makes them integration tests. If your test
requires a running MAPDL instance, you can use the PyMAPDL
`mapdl <mapdl_fixture_>`_ method in your function signature.
It will be executed upstream of each test and not within all tests.

.. code:: python

   def test_my_new_feature(mapdl):  # pass the 'mapdl' fixture as an argument.
       mapdl.prep7()
       # .... more code

       return True  # if everything goes ok until here


Example
--------

The `test_math.py <pymapdl_test_math_>`_ file contains the unit tests and integration tests of the `ansys.mapdl.core.math module <pymapdl_user_guide_math_>`_. These are just some of the many
tests that you can find in the `test directory <pymapdl_tests_>`_.

Here are some examples of how you use ``pytest``:

.. code:: python

    import numpy as np
    import ansys.mapdl.core.math as apdl_math


    @pytest.fixture(scope="module")
    def mm(mapdl):  # pass the 'mapdl' fixture as an argument.
        return mapdl.math


    def test_rand(mm):  # pass the 'mm' fixture as an argument.
        w = mm.rand(10)
        assert w.size == 10  # if it is False, AssertionError is raised


    def test_matrix_addition(mm):
        m1 = mm.rand(10, 10)
        m2 = mm.rand(10, 10)
        m3 = m1 + m2
        assert np.allclose(m1.asarray() + m2.asarray(), m3.asarray())
        # if it is False, AssertionError is raised

For further explanations, see the `pytest documentation <pytest_>`_.