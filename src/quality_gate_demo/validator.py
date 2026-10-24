"""Small input-validation helpers used as real code for the CI quality gate.

The module is intentionally small: the point of this repository is the
quality gate around the code, not the code itself. Every rule raises a
:class:`ValidationError` carrying a stable machine-readable code so tests
and callers can branch on the failure reason instead of the message.
"""

from __future__ import annotations

import string
from collections.abc import Iterable
from typing import Final

__all__ = [
    "ValidationError",
    "validate_email",
    "validate_password",
    "validate_port",
    "validate_project_name",
]

_NAMESPACE_CHARS: Final = set(string.ascii_letters + string.digits + "-_")
_SPECIAL_CHARS: Final = set(string.punctuation)
_RESERVED_NAMES: Final[frozenset[str]] = frozenset(
    {"admin", "root", "support", "null", "undefined"}
)

NAME_MIN_LENGTH: Final = 3
NAME_MAX_LENGTH: Final = 64
PORT_MIN: Final = 1
PORT_MAX: Final = 65535
EMAIL_LOCAL_MAX: Final = 64
EMAIL_MAX_LENGTH: Final = 254
PASSWORD_MIN_LENGTH: Final = 12


class ValidationError(ValueError):
    """Raised when an input violates a validation rule.

    Attributes:
        field: The logical field that failed validation (for example
            ``"email"``), useful in API responses and tests.
        code: A stable, machine-readable reason such as ``"too_short"``.
    """

    def __init__(self, field: str, code: str, message: str) -> None:
        super().__init__(message)
        self.field = field
        self.code = code


def validate_project_name(name: str) -> str:
    """Validate a project name and return it unchanged.

    Rules: stripped length between 3 and 64, only letters, digits,
    ``-`` and ``_``, and no reserved name (case-insensitive).
    """
    if not isinstance(name, str):
        raise ValidationError("name", "not_a_string", "project name must be a string")
    if not name.strip():
        raise ValidationError("name", "empty", "project name must not be empty")
    trimmed = name.strip()
    if len(trimmed) < NAME_MIN_LENGTH:
        raise ValidationError("name", "too_short", f"shorter than {NAME_MIN_LENGTH}")
    if len(trimmed) > NAME_MAX_LENGTH:
        raise ValidationError("name", "too_long", f"longer than {NAME_MAX_LENGTH}")
    if not set(trimmed) <= _NAMESPACE_CHARS:
        raise ValidationError(
            "name",
            "invalid_characters",
            "only letters, digits, '-' and '_' are allowed",
        )
    if trimmed.lower() in _RESERVED_NAMES:
        raise ValidationError("name", "reserved", f"'{trimmed.lower()}' is reserved")
    return trimmed


def validate_port(port: int | str) -> int:
    """Validate a TCP port given as int or decimal string and return it as int.

    Accepts ``int`` or a string of digits (an optional surrounding "+"/"-"
    is rejected). Valid values are 1..65535.
    """
    if isinstance(port, str):
        if not port.isascii() or not port.isdigit():
            raise ValidationError(
                "port", "not_an_integer", "port must be a decimal digit string"
            )
        value = int(port)
    elif isinstance(port, int) and not isinstance(port, bool):
        value = port
    else:
        raise ValidationError(
            "port", "unsupported_type", "port must be an int or a digit string"
        )
    if not PORT_MIN <= value <= PORT_MAX:
        raise ValidationError(
            "port", "out_of_range", f"port must be between {PORT_MIN} and {PORT_MAX}"
        )
    return value


def validate_email(email: str) -> str:
    """Validate a simplified email address and return it lowercased.

    The check is intentionally local (no DNS): one ``@``, non-empty local
    part (max 64), a domain with at least one dot, no spaces, total length
    <= 254.
    """
    if not isinstance(email, str):
        raise ValidationError("email", "not_a_string", "email must be a string")
    value = email.strip()
    if not value:
        raise ValidationError("email", "empty", "email must not be empty")
    if len(value) > EMAIL_MAX_LENGTH:
        raise ValidationError("email", "too_long", f"longer than {EMAIL_MAX_LENGTH}")
    if " " in value:
        raise ValidationError(
            "email", "contains_space", "email must not contain spaces"
        )
    if value.count("@") != 1:
        raise ValidationError(
            "email", "missing_at", "email must contain exactly one '@'"
        )
    local, _, domain = value.partition("@")
    if not local:
        raise ValidationError("email", "empty_local", "local part must not be empty")
    if len(local) > EMAIL_LOCAL_MAX:
        raise ValidationError(
            "email", "local_too_long", f"local part longer than {EMAIL_LOCAL_MAX}"
        )
    if "." not in domain or domain.count(".") < 1 or ".." in domain:
        raise ValidationError("email", "invalid_domain", "domain must contain a dot")
    if domain.startswith(".") or domain.endswith("."):
        raise ValidationError(
            "email", "invalid_domain", "domain must not start or end with a dot"
        )
    return value.lower()


def validate_password(password: str) -> str:
    """Validate a password and return it unchanged.

    Rules: at least 12 characters, and containing at least one lowercase
    letter, one uppercase letter, one digit and one character from
    ``string.punctuation``.
    """
    if not isinstance(password, str):
        raise ValidationError("password", "not_a_string", "password must be a string")
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(
            "password",
            "too_short",
            f"password must be at least {PASSWORD_MIN_LENGTH} characters",
        )
    missing = _missing_categories(password)
    if missing:
        raise ValidationError(
            "password", "missing_category", "missing: " + ", ".join(missing)
        )
    return password


def _missing_categories(password: str) -> list[str]:
    """Return the character categories not present in ``password``."""
    checks: tuple[tuple[Iterable[str], str], ...] = (
        (string.ascii_lowercase, "lowercase"),
        (string.ascii_uppercase, "uppercase"),
        (string.digits, "digit"),
        (_SPECIAL_CHARS, "special"),
    )
    return [
        label
        for characters, label in checks
        if not any(char in password for char in characters)
    ]
