"""
api/__init__.py

API routers package for OptIn Manager.

This package contains all the API endpoints for the OptIn Manager backend,
organized into modules by resource type. It implements the RESTful API that
the frontend interacts with to manage opt-in programs, contacts, consents,
and other resources.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

# Import submodules to make them available when the package is imported
from . import preferences
