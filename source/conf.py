# SPDX-FileCopyrightText: © 2020 Matt Williams <matt@milliams.com>
# SPDX-License-Identifier: MIT

# -- Project information -----------------------------------------------------

project = "Bristol RSE"
copyright = "2021, Bristol RSE Team. CC-BY-SA 4.0"
author = ""


# -- General configuration ---------------------------------------------------

extensions = [
    # incompatible with Sphinx 4 https://github.com/executablebooks/MyST-Parser/issues/378 "myst_parser",
]

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv"]


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/BristolRSE/bristolrse.github.io",
    "path_to_docs": "source",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_fullscreen_button": False,
    "extra_navbar": "",
    "search_bar_text": "Search...",
}

html_static_path = ["_static"]

# This sets the default behaviour of plain single ticks like `this`. 
# The "any" role is documented at https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-any
# The "literal" role: https://docutils.sourceforge.io/docs/ref/rst/roles.html#literal
default_role = "literal"
