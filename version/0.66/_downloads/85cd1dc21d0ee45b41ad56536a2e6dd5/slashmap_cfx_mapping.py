"""
.. _ref_cfx_mapping:

=============================================
CFX pressure data mapping to structural blade
=============================================

The objective of this test is to demonstrate CFX pressure data mapping to
structural 11 blade model in PyMAPDL.

Description
===========

The 11 blade model along with a fictitious disk is modeled. CFX generated
pressure data is used as input.

The test uses a CFX exported pressure data to map. Pressure file
correspond to a certain vibrating blade mode (vibrating mode 1
approximately 534 Hz)and to a certain pressure mode (pressure mode 1
also the same 534 Hz mode). However, due to lack of data for another
mode this same file will be assumed to represent other mode
combinations (vib mode 2 press mode 2) (vib mode 1 press mode 2)
(vib mode 2 press mode 1).

"""

from datetime import datetime

from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.examples import download_cfx_mapping_example_data

###############################################################################
# Downloading files
# =================
#
files_path = download_cfx_mapping_example_data()

db_file_path = files_path["model"]
pressure_file_path = files_path["data"]

###############################################################################
# Launch MAPDL service
# ====================
#

mapdl = launch_mapdl()

mapdl.title(
    "Verify Pressure Data Mapping exported from CFX on Structural 11 Blade Model"
)

###############################################################################
# Upload files to the instance
# ============================
#
# Uploading files
mapdl.upload(db_file_path)
mapdl.upload(pressure_file_path)


###############################################################################
# Pressure mapping
# ================
#
# Resume the database from the example mapping file
mapdl.resume("ExampleMapping", "db")
mapdl.esel("s", "type", "", 1)
mapdl.cm("BladeElem", "elem")

# Write CDB file
mapdl.allsel()
mapdl.cdwrite("all", "baseModel", "cdb")
mapdl.finish()

# Start the mapping processor and record the start time
start_time = datetime.now()
mapdl.slashmap()  # mapdl.slashmap(**kwargs); Enters the mapping processor.
print("Enter the Mapping Processor")

# Specifies the target nodes for mapping pressures onto surface effect elements.
mapdl.run("target,pressure_faces")

# Specifies the file type and pressure type for the subsequent import of source points and pressures.
mapdl.ftype(filetype="cfxtbr", prestype="1")
# Read the CFX exported file containing pressure data Blade 2, Export Surface 1
mapdl.read(fname="11_blades_mode_1_ND_0.csv")

# Perform the pressure mapping from source points to target surface elements.
# Interpolation is done on a surface (default).
print(mapdl.map(kdim="2", kout="1"))

###############################################################################
# Plot mapping
# ============
#
# Plot the geometries and mappings
mapdl.show("png,rev")
mapdl.plgeom(item="BOTH")  # Plot both target and source geometries (default).
mapdl.plmap(item="target")
mapdl.plmap(item="target", imagkey="1")
mapdl.plmap(item="source")
mapdl.plmap(item="source", imagkey="1")
mapdl.plmap(item="both")
mapdl.plmap(item="both", imagkey="1")

# Close the plot and write the mapped data to a file
mapdl.show("close")
mapdl.writemap("mappedHI.dat")

# Print the mapping completion message and duration
print("Mapping Completed")
end_time = datetime.now()
c = end_time - start_time
seconds = c.total_seconds()
print("\nDuration in seconds for Mapping is  : ", seconds)

mapdl.eplot()

###############################################################################
# Stop MAPDL
#
mapdl.finish()
mapdl.exit()
