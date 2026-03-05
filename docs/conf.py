"""Sphinx configuration"""

extensions = [
    "autodoc2",                   # Auto-generate API docs
    'myst_parser',                # Accept Markdown as input.
    'sphinx.ext.viewcode',        # Include highlighted source code.
    'sphinx.ext.intersphinx',     # Support short-hand web links.
    'sphinx.ext.napoleon',        # Google-style docstrings
]

# Meta information
project    = 'Pipe-Cleaner'
html_title = project

# Source parsing
root_doc = 'index'                     # start page
nitpicky = True                        # Warn about missing references?

# Short-hand web links
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# Code documentation
autodoc2_render_plugin = "myst"
autodoc2_packages = [
    "../src/pipe_cleaner",
]
# Only show public API docs
autodoc2_module_all_regexes = [
    r"pipe_cleaner\..*",
]
autodoc2_output_dir = "api"

# Rendering options
html_show_copyright = False            # Show copyright notice in footer?
html_show_sphinx    = True             # Show Sphinx blurb in footer?
html_copy_source    = True             # Copy documentation source files?
html_theme          = 'furo'           # custom theme with light and dark mode
pygments_style      = 'friendly'       # syntax highlight style in light mode
pygments_dark_style = 'stata-dark'     # syntax highlight style in dark mode
