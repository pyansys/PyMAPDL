"""
.. _ref_dpf_basic_example:

Basic DPF-Core Usage with PyMAPDL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example is adapted from
`Basic DPF-Core Usage Example <https://dpf.docs.pyansys.com/version/stable/examples/00-basic/00-basic_example.html>`_
and it shows how to open a result file in `DPF <https://dpf.docs.pyansys.com/>`_ and do some
basic postprocessing.

If you have Ansys 2021 R1 installed, starting DPF is quite easy
as DPF-Core takes care of launching all the services that
are required for postprocessing Ansys files.

First, import the DPF-Core module as ``dpf_core`` and import the
included examples file.


"""
import tempfile

from ansys.dpf import core as dpf

from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.examples import vmfiles

###############################################################################
# Create model
# ~~~~~~~~~~~~~~
#
# Running an example from the MAPDL verification manual
#
mapdl = launch_mapdl()

vm5 = vmfiles["vm5"]
output = mapdl.input(vm5)

print(output)

# If you are working locally, you don't need to perform the following steps
temp_directory = tempfile.gettempdir()

# Downloading RST file to the current folder
rst_path = mapdl.download_result(temp_directory)

###############################################################################
# Next, open the generated RST file and print out the
# :class:`Model <ansys.dpf.core.model.Model>` object.
# The :class:`Model <ansys.dpf.core.model.Model>` class helps to
# organize access methods for the result by
# keeping track of the operators and data sources used by the result
# file.
#
# Printing the model displays:
#
# - Analysis type
# - Available results
# - Size of the mesh
# - Number of results

###############################################################################
# If you are working with a remote server, you might need to upload the ``RST``
# file before working with it.
# Then you can create the :class:`DPF Model <ansys.dpf.core.model.Model>`.

dpf.core.make_tmp_dir_server(dpf.SERVER)

if dpf.SERVER.local_server:
    model = dpf.Model(rst_path)
else:
    server_file_path = dpf.upload_file_in_tmp_folder(rst_path)
    model = dpf.Model(server_file_path)

print(model)

###############################################################################
# Model Metadata
# ~~~~~~~~~~~~~~
# Specific metadata can be extracted from the model by referencing the
# model's :attr:`metadata <ansys.dpf.core.model.Model.metadata>`
# property.  For example, to print only the
# :attr:`result_info <ansys.dpf.core.model.Metadata.result_info>`:

metadata = model.metadata
print(metadata.result_info)

###############################################################################
# To print the :class:`mesh region<ansys.dpf.core.meshed_region.MeshedRegion>`:

print(metadata.meshed_region)

###############################################################################
# To print the time or frequency of the results use
# :class:`time_freq_support <ansys.dpf.core.time_freq_support.TimeFreqSupport>`:

print(metadata.time_freq_support)

###############################################################################
# Extracting Displacement Results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# All results of the model can be accessed through the :class:`Results <ansys.dpf.core.results.Results>`
# property, which returns the :class:`ansys.dpf.core.results.Results`
# class. This class contains the DPF result operators available to a
# specific result file, which are listed when printing the object with
# ``print(results)``.
#
# Here, the :class:`displacement <ansys.dpf.core.operators.result.displacement.displacement>`
# operator is connected with
# :class:`DataSources <ansys.dpf.core.data_sources.DataSources>`, which
# takes place automatically when running
# :class:`results.displacement() <ansys.dpf.core.operators.result.displacement.displacement>`.
# By default, the :class:`displacement <ansys.dpf.core.operators.result.displacement.displacement>`
# operator is connected to the first result set,
# which for this static result is the only result.

results = model.results
displacements = results.displacement()
fields = displacements.outputs.fields_container()

# Finally, extract the data of the displacement field:
disp = fields[0].data
disp

###############################################################################
# Plot displacements
# ~~~~~~~~~~~~~~~~~~
#
# You can plot the previous displacement field using:

model.metadata.meshed_region.plot(fields, cpos="xy")

###############################################################################
# Or using
#

fields[0].plot(cpos="xy")

###############################################################################
# This way is particularly useful if you have used :class:`ansys.dpf.core.scoping.Scoping`
# on the mesh or results.


###############################################################################
# Close session
# ~~~~~~~~~~~~~~
#
# Stop MAPDL session.
#
mapdl.exit()
