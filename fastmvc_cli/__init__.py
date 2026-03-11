"""
FastMVC CLI - Command Line Interface for FastMVC Framework.

This package provides CLI tools to generate new FastAPI projects
based on the FastMVC architecture pattern.

Usage:
    $ pip install pyfastmvc
    $ fastmvc generate <project_name>
    $ fastmvc add entity <entity_name>
    $ fastmvc migrate upgrade

Example:
    $ fastmvc generate my_awesome_api
    $ cd my_awesome_api
    $ pip install -r requirements.txt
    $ fastmvc migrate upgrade
    $ python -m uvicorn app:app --reload
"""

__version__ = "1.2.0"
__author__ = "FastMVC Team"
__package_name__ = "pyfastmvc"

