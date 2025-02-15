"""Sphinx documentation configuration file."""

from datetime import datetime
import os
from pathlib import Path
import sys
import warnings

import ansys.tools.visualization_interface as viz_interface
from ansys_sphinx_theme import ansys_favicon, get_version_match
import numpy as np
import pyvista
from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx_gallery.sorting import FileNameSortKey

from ansys.mapdl import core as pymapdl
from ansys.mapdl.core import __version__

# Convert notebooks into Python scripts and include them in the output files
logger = logging.getLogger(__name__)

viz_interface.DOCUMENTATION_BUILD = True
pyvista.BUILDING_GALLERY = True
pyvista.OFF_SCREEN = True

# Manage errors
pyvista.set_error_output_file("errors.txt")

# Ensure that offscreen rendering is used for docs generation

# must be less than or equal to the XVFB window size
try:
    pyvista.global_theme.window_size = np.array([1024, 768])
except AttributeError:
    # for compatibility with pyvista < 0.40
    pyvista.rcParams["window_size"] = np.array([1024, 768])

# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath("./images/"), "auto-generated/")
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

# necessary when building the sphinx gallery
pyvista.BUILDING_GALLERY = True
pymapdl.BUILDING_GALLERY = True

# suppress annoying matplotlib bug
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.",
)

# To allow using 'helper' python file as a module
sys.path.append(os.path.dirname(__file__))


# -- Project information -----------------------------------------------------

project = "ansys-mapdl-core"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS Inc."

# The short X.Y version
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "mapdl.docs.pyansys.com")
switcher_version = get_version_match(__version__)

REPOSITORY_NAME = "pymapdl"
USERNAME = "ansys"
BRANCH = "main"

DEFAULT_EXAMPLE_EXTENSION = "py"

DOC_PATH = "doc/source"
GALLERY_EXAMPLES_PATH = "examples/gallery_examples"
EXAMPLES_ROOT = "examples"
EXAMPLES_PATH_FOR_DOCS = f"../../{EXAMPLES_ROOT}/"

SEARCH_HINTS = ["def", "class"]

SOURCE_PATH = Path(__file__).parent.resolve().absolute()
pyansys_light_mode_logo = str(
    os.path.join(SOURCE_PATH, "_static", "pyansys-logo-light_mode.png")
)

# -- General configuration ---------------------------------------------------
extensions = [
    "jupyter_sphinx",
    "numpydoc",
    "pyvista.ext.viewer_directive",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx_design",
    "sphinx_jinja",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
    "sphinxemoji.sphinxemoji",
    "sphinx.ext.graphviz",
    "ansys_sphinx_theme.extension.linkcode",
    "sphinx.ext.mathjax",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "pyvista": ("https://docs.pyvista.org", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    "pypim": ("https://pypim.docs.pyansys.com/version/dev/", None),
    "ansys-dpf-core": ("https://dpf.docs.pyansys.com/version/stable/", None),
    "ansys-math-core": ("https://math.docs.pyansys.com/version/stable/", None),
    "ansys-tools-path": ("https://path.tools.docs.pyansys.com/version/stable/", None),
}

suppress_warnings = ["label.*", "design.fa-build", "config.cache"]
sd_fontawesome_latex = True

# Graphviz diagrams configuration
graphviz_output_format = "png"

# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    # "GL06",  # Found unknown section
    # "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

numpydoc_validation_exclude = {  # set of regex
    # class inherits from pymapdl-reader
    r"\.*MeshGrpc\.*",
}

# Favicon
html_favicon = ansys_favicon

# notfound.extension
notfound_template = "404.rst"
notfound_urls_prefix = "/../"
html_baseurl = f"https://{cname}/version/stable"

# static path
html_static_path = ["_static"]

html_css_files = [
    "custom.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
]

panels_add_fontawesome_latex = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # because we include this in examples/index.rst
    f"{GALLERY_EXAMPLES_PATH}/index.rst",
    "links.rst",
    "substitutions.rst",
]

# make rst_epilog a variable, so you can add other epilog parts to it
rst_epilog = ""

# Read link all targets from file
with open("links.rst") as f:
    rst_epilog += f.read()

rst_epilog = rst_epilog.replace("%%VERSION%%", "v242")
rst_epilog = rst_epilog.replace("%%PYMAPDLVERSION%%", release)


# Read link all substitutions from file
with open("substitutions.rst") as f:
    rst_epilog += f.read()

# Broken anchors:
linkcheck_exclude_documents = ["index", "changelog"]
linkcheck_anchors_ignore_for_url = ["https://docs.pyvista.org/api/*"]
linkcheck_ignore = [
    "https://github.com/ansys/pymapdl/*",
    "https://mapdl.docs.pyansys.com/*",
    "https://www.ansys.com/*",  # behind firewall
    "https://download.ansys.com/*",  # behind firewall
    "https://ansysaccount.b2clogin.com/*",  # behind authentication
    "https://ansyshelp.ansys.com/*",  # behind authentication
    "https://forum.ansys.com/forums/*",  # It is detected as broken
    "https://courses.ansys.com/*",  # It is detected as broken
]
linkcheck_anchors_ignore = [
    # these anchors are picked by linkcheck as broken but they are not.
    "firewall-rules",
    "pyvista.Plotter",
    "pyvista.UnstructuredGrid",
    "pyvista.Plotter.show",
]

# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
if switcher_version != "dev":
    linkcheck_ignore.append(
        f"https://github.com/ansys/pymapdl/releases/tag/v{__version__}"
    )

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81"  # noqa: E501

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True

# -- Sphinx Gallery Options ---------------------------------------------------
sphinx_gallery_conf = {
    # convert rst to md for ipynb
    "pypandoc": True,
    # path to your examples scripts
    "examples_dirs": [EXAMPLES_PATH_FOR_DOCS],
    # path where to save gallery generated examples
    "gallery_dirs": [GALLERY_EXAMPLES_PATH],
    # Pattern to search for example files
    "filename_pattern": r"\." + DEFAULT_EXAMPLE_EXTENSION,
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": FileNameSortKey,
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created.  In
    "doc_module": "ansys-mapdl-core",
    "image_scrapers": (DynamicScraper(), "matplotlib"),
    "ignore_pattern": "flycheck*",
    "thumbnail_size": (350, 350),
    "remove_config_comments": True,
    "default_thumb_file": pyansys_light_mode_logo,
    "show_signature": False,
}
# ---


# -- Options for HTML output -------------------------------------------------
html_short_title = html_title = "PyMAPDL"
html_theme = "ansys_sphinx_theme"
html_theme_options = {
    "logo": "pyansys",
    "analytics": {"google_analytics_id": "G-JQJKPV6ZVB"},
    "github_url": f"https://github.com/{USERNAME}/{REPOSITORY_NAME}",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "navigation_with_keys": False,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": f"https://github.com/{USERNAME}/{REPOSITORY_NAME}/discussions",
            "icon": "fa fa-comment fa-fw",
        },
        {
            "name": "Contribute",
            "url": "https://mapdl.docs.pyansys.com/version/dev/getting_started/contribution.html",
            "icon": "fa fa-wrench",
        },
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
}

BUILD_CHEATSHEET = os.environ.get("BUILD_CHEATSHEET", "false").lower() == "true"

if BUILD_CHEATSHEET:
    html_theme_options["cheatsheet"] = {
        "file": "cheat_sheet/cheat_sheet.qmd",
        "title": "PyMAPDL cheat sheet",
        "version": f"v{version}",
        "pages": ["getting_started/learning"],
    }

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": USERNAME,
    "github_repo": REPOSITORY_NAME,
    "github_version": BRANCH,
    "doc_path": str(DOC_PATH),
    "source_path": "src",
}
html_show_sourcelink = False

html_sidebars = {
    "mapdl_commands/**/**": [],
    "mapdl_commands/index": [],
}

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "pymapdldoc"


# -- Options for LaTeX output ------------------------------------------------
latex_elements = {}

latex_engine = "xelatex"

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        f"pymapdl-Documentation-{__version__}.tex",
        "ansys.mapdl.core Documentation",
        author,
        "manual",
    ),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        master_doc,
        "ansys.mapdl.core",
        "ansys.mapdl.core Documentation",
        [author],
        1,
    )
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "ansys.mapdl.core",
        "ansys.mapdl.core Documentation",
        author,
        "ansys.mapdl.core",
        "Pythonic interface to MAPDL using gRPC",
        "Engineering Software",
    ),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


def setup(app: Sphinx):
    """Add custom configuration to sphinx app.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application.
    """

    # Adding apdl syntax highlighting
    from pygments.lexers.apdlexer import apdlexer
    from pygments.lexers.julia import JuliaLexer

    # ANSYS lexer
    app.add_lexer("apdl", apdlexer)
    app.add_lexer("ansys", apdlexer)

    # Julia lexer
    app.add_lexer("julia", JuliaLexer)

    # Setting custom directive
    from helpers import HideObject

    app.add_directive("hideobject", HideObject)


jinja_contexts = {
    "cheat_sheet": {"version": switcher_version},
}
