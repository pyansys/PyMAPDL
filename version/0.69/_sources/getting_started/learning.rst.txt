.. _ref_learning:

================
Learning PyMAPDL
================

Introduction
============

.. centered:: *PyMAPDL provides Pythonic access to MAPDL, an Ansys finite element solver.*

PyMAPDL touches on different technologies such as Python and finite elements, to bring them together
and offer you a better user experience by seamlessly connecting this Ansys solver and the Python ecosystem.
To learn how to use this library, you have many resources available:

* Complete the :ref:`ref_pymapdl_course` course, which guides you through PyMAPDL's
  main functionalities.
* Visit the `Examples gallery <pymapdl_examples_gallery_>`_ to learn from practical examples.
  The `Static analysis of a corner bracket <pymapdl_bracket_static_example_>`_ example is a very
  good starting point.
* Become familiar with the Python programming language. There are many online courses and
  websites for learning Python. Additionally, Ansys provides a :ref:`ref_python_course` course.
* Understand finite element methods (FEMs). Because physical models are solved using FEMs, you
  need to know how these methods work to get accurate and adequate solutions. The 
  `Introduction to Finite Element Methods <course_fem_track_>`_ course on the Ansys
  Learning Resources website offers tracks to help you to get familiar with these methods.
* Take the Ansys :ref:`ref_mapdl_course` course. Because PyMAPDL interface with MAPDL
  through APDL commands, you should become familiar with MAPDL commands and
  workflows.

.. _ref_additional_learning:

Downloads
=========

- You can try the Student Version of Ansys products. For more information, see
  `Ansys Student Versions <ansys_student_version_>`_.
  These are versions valid during a year and with limited capabilities 
  regarding number of nodes, elements, etc.

.. jinja:: cheat_sheet
  
  - View and download :download:`PyMAPDL cheatsheet <https://github.com/ansys/pymapdl/blob/gh-pages/version/{{ version }}/_static/cheat_sheet.pdf>`  
    to help you to learn PyMAPDL.

- Visit :ref:`ref_examples` to learn how PyMAPDL can be used to solve different real problems.


Courses
=======

Ansys has prepared high quality courses to guide you through the learning process.


.. _ref_python_course:

Intro to Python
---------------

The `Intro to Python <course_intro_python_>`_ course teaches you
the basis of the Python programming language.


Course content
~~~~~~~~~~~~~~

* Prerequisites - Installation of Python
* Fundamentals of Python - Lesson 1
* Analyzing Radiance Data - Lesson 2
* Repeating Actions with Loops - Lesson 3
* Storing Multiple Values in Lists - Lesson 4
* Making Choices - Lesson 5
* Analyzing Data from Multiple Files - Lesson 6
* Creating Functions - Lesson 7
* Defensive Programming - Lesson 8
* Debugging - Lesson 9
* Command Line Programs - Lesson 10
* Post Completion Survey
* Meet the Instructor


.. _ref_pymapdl_course:

Getting started with PyMAPDL
----------------------------

The `Getting started with PyMAPDL <course_getting_started_pymapdl_>`_ course teaches
you about PyMAPDL, the Pythonic way to access Ansys MAPDL. 

Course content
~~~~~~~~~~~~~~

* Overview of PyMAPDL - Lesson 1
* PyMAPDL Language and Usage - Lesson 2
* PyMAPDL Categories - Lesson 3
* Getting Help - Lesson 4
* Post Completion Survey
* Meet the Instructors

.. _ref_mapdl_course:

Intro to Ansys Mechanical APDL scripting
----------------------------------------

The `Intro to Ansys Mechanical APDL scripting <course_intro_apdl_>`_
course teaches you how APDL, the Mechanical solver syntax language, works.

Course content
~~~~~~~~~~~~~~

* Overview of MAPDL (Lesson 1)
* Basics of APDL Language (Lesson 2)
* Solid Modeling & Meshing (Lesson 3)
* Defining Loads, BCs, and Solver Controls (Lesson 4)
* General Postprocessing (Lesson 5)
* Selection Logic (Lesson 6)
* More on Parameters (Arrays, \*GET) (Lesson 7)
* Post Completion Survey
* Meet the Instructors

.. vale off

Ansys Innovation Space
----------------------

.. vale on

You can find more courses for different Ansys product organized in 
different categories such as
`structures <ansys_innovation_space_structures_>`_,
`fluids <ansys_innovation_space_fluids_>`_,
`materials <ansys_innovation_space_materials_>`_ or
`3D design <ansys_innovation_space_geometry_>`_. 

You can find all the categories in `https://courses.ansys.com <ansys_innovation_space_>`_.

**NOTE**: You might need to create a free Ansys account to access these resources.

Ansys help
==========

`Ansys Help <ansys_help_>`_ is the official Ansys website for
documentation, tutorials and videos.

An `MAPDL introductory tutorials guide <ansys_introductory_mapdl_courses_>`_ which
cover different topics such as
`Structural tutorial <ansys_introtut_structures_>`_
`Thermal tutorial <ansys_introtut_thermal_>`_
`Electromagnetics tutorial <ansys_introtut_electromag_>`_
`Micro-Electromechanical System (MEMS) tutorial <ansys_introtut_mems_>`_
`Contact tutorial <ansys_introtut_contact_>`_ or
`Modal tutorial <ansys_introtut_modal_>`_

You can find documentation such as the
`Command reference guide <ansys_command_reference_guide_>`_,
`Verification manual guide <ansys_verification_manual_>`_ or
`Technology showcase guide <ansys_techdemo_guide_>`_.

The `Technology showcase guide <ansys_techdemo_guide_>`_ is a comprehensive guide with 
real-world example problems which present the broad simulation
capabilities of Ansys Mechanical APDL.
The problems demonstrate how to use Mechanical APDL to effectively 
and accurately solve interdisciplinary problems from a variety of
industries and engineering fields.
The problems are more substantive and complex than examples found
in the standard documentation set. The documentation thoroughly
examines the physics involved with each problem and the considerations
necessary for translating problems into numerical models.
You can find some of the technology showcase examples in PyMAPDL documentation 
`Technology Showcases <pymapdl_ex_ts_>`. For a more comprehensive list of
showcases, visit `Technology showcase guide <ansys_techdemo_guide_>`_.

**NOTE**: You might need to create a free Ansys account to access these resources.


Additional resources
====================

Ansys has prepared multiple resources to help you to learn and use PyMAPDL.
You can access them from the `Ansys Learning Resources <learning_resources_>`_ website.
In this website, you can find a summary of the available resources for MAPDL and PyMAPDL.


Recommended articles
====================

.. vale off

* Ansys Gets Into Open Source With GitHub.
  `Link to article in Ansys Blog <ansys_open_source_article_>`_
* Access the Power of Ansys from the Python World.
  `Link to article in Ansys blog <ansys_python_power_article_>`_
* Using Ansys Scripting with pyMAPDL, pyDPF-Post, and More - Part 1
  *Running and Post-Processing an Ansys Model Outside Ansys*. 
  `Link to article in PADT Inc Blog <padt_post_>`_.
* ANSYS in a Python Web App, Part 1: Post Processing with PyDPF:
  *Integrating PyAnsys with Plotly's Dash and the Dash-VTK component to build an
  Ansys structural analysis post-processing web application*.
  `Link to 'Towards Data Science' article in Medium <tds_article_web_app_1_>`_.
* ANSYS in a Python Web App, Part 2: Pre Processing & Solving with PyMAPDL:
  *ANSYS in a Python Web App, Part 2: Pre Processing & Solving with PyMAPDL*.
  `Link to 'Towards Data Science' article in Medium <tds_article_web_app_2_>`_.
* Paraview: Reading ANSYS APDL (RST) results in Paraview.
  `Link to 'Paraview Forum' question <paraview_question_read_rst_>`_.

.. vale on

Feel free to share any educational or learning resources by `opening an issue <pymapdl_issues_>`_
or `starting a discussion <pymapdl_discussions_>`_ on GitHub.
