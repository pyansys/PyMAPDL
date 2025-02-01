.. _post_processing_api:


``PostProcessing`` class
========================

The ``PostProcessing`` class supports postprocessing directly from the MAPDL live instance.
If you want to postprocess MAPDL result files outside of PyMAPDL,
you can use one of these packages:

* `PyDPF-Core <dpf_core_docs_>`_ : Postprocessing using the Data Processing Framework (DPF). DPF-Core provides more complex and more powerful postprocessing APIs.
* `PyDPF-Post <dpf_post_docs_>`_ : Streamlined and simplified DPF postprocessing. PyDPF-Post is a higher-level package that uses PyDPF-Core.
* `PyMAPDL Reader <legacy_reader_docs_>`_: Legacy result file reader. PyMAPDL Reader supports result files for MAPDL 14.5 and later.

.. currentmodule:: ansys.mapdl.core

.. autosummary::
   :toctree: _autosummary

   post.PostProcessing
