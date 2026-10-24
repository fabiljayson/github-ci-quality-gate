"""quality_gate_demo - a small validation package used as CI exercise material.

The package exists to give the GitHub Actions quality gate real code,
tests, and lint targets. It has zero runtime dependencies.
"""

from quality_gate_demo.validator import (
    ValidationError,
    validate_email,
    validate_password,
    validate_port,
    validate_project_name,
)

__version__ = "0.1.0"

__all__ = [
    "ValidationError",
    "__version__",
    "validate_email",
    "validate_password",
    "validate_port",
    "validate_project_name",
]
