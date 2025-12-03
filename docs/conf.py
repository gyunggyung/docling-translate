# Configuration file for the Sphinx documentation builder.

import os
import sys
from pathlib import Path

# -- Project information -----------------------------------------------------
project = 'Docling Translate'
copyright = '2025, Docling Translate Team'
author = 'Docling Translate Team'
release = '1.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- MyST Parser configuration -----------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

# -- Internationalization ----------------------------------------------------
language = 'ko'
