"""Edge-case and regression tests for the quality_gate_demo validators.

These tests document behaviour that is deliberately chosen rather than
accidental: type handling, boundaries, error identity and validation
interaction between fields.
"""

import pytest

from quality_gate_demo import (
    ValidationError,
    validate_email,
    validate_password,
    validate_port,
    validate_project_name,
)


class TestTypeHandling:
    """Non-str inputs must fail with not_a_string, never TypeError."""

    @pytest.mark.parametrize(
        "caller",
        [
            lambda: validate_project_name(None),  # type: ignore[arg-type]
            lambda: validate_email(b"alice@example.org"),  # type: ignore[arg-type]
            lambda: validate_password(["S3cure!Passw0rd"]),  # type: ignore[arg-type]
        ],
    )
    def test_wrong_type_raises_validation_error(self, caller) -> None:
        with pytest.raises(ValidationError) as excinfo:
            caller()
        assert excinfo.value.code == "not_a_string"

    def test_bool_is_not_a_valid_port(self) -> None:
        # bool is a subclass of int; it must not sneak through.
        with pytest.raises(ValidationError) as excinfo:
            validate_port(True)
        assert excinfo.value.code == "unsupported_type"


class TestBoundaries:
    def test_port_upper_boundary_is_inclusive(self) -> None:
        assert validate_port(65535) == 65535

    def test_port_just_above_boundary_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            validate_port(65536)

    def test_name_boundary_64_accepted_65_rejected(self) -> None:
        assert validate_project_name("x" * 64) == "x" * 64
        with pytest.raises(ValidationError):
            validate_project_name("x" * 65)

    def test_email_local_part_boundary_64_accepted(self) -> None:
        local = "a" * 64
        assert validate_email(f"{local}@example.org") == f"{local}@example.org"

    def test_email_254_accepted_and_255_rejected(self) -> None:
        # The 64-char local-part cap means the 254-char boundary must be
        # reached through a long domain, not a long local part.
        email_ok = "u@" + "a" * 248 + ".com"  # 1 + 1 + 252 = 254 chars
        assert len(email_ok) == 254
        assert validate_email(email_ok) == email_ok
        with pytest.raises(ValidationError):
            validate_email("u@" + "a" * 249 + ".com")  # 255 chars

    def test_password_min_length_is_inclusive(self) -> None:
        assert validate_password("Aa1!Aa1!Aa1!")


class TestValidationErrorIdentity:
    def test_subclasses_value_error(self) -> None:
        assert issubclass(ValidationError, ValueError)

    def test_catchable_as_value_error(self) -> None:
        with pytest.raises(ValueError):
            validate_project_name(None)  # type: ignore[arg-type]

    def test_code_stable_across_calls(self) -> None:
        for _ in range(2):
            with pytest.raises(ValidationError) as excinfo:
                validate_email("broken")
            assert excinfo.value.code == "missing_at"

    def test_field_attribute_points_to_caller_field(self) -> None:
        with pytest.raises(ValidationError) as excinfo:
            validate_password("short")
        assert excinfo.value.field == "password"
        assert excinfo.value.code == "too_short"


class TestInteractionBetweenFields:
    def test_valid_inputs_compose_into_a_record(self) -> None:
        record = {
            "name": validate_project_name("csv-doctor"),
            "port": validate_port("8000"),
            "email": validate_email("Dev@Example.ORG"),
            "password": validate_password("S3cure!Passw0rd"),
        }
        assert record == {
            "name": "csv-doctor",
            "port": 8000,
            "email": "dev@example.org",
            "password": "S3cure!Passw0rd",
        }

    def test_invalid_field_does_not_corrupt_valid_fields(self) -> None:
        name = validate_project_name("csv-doctor")
        with pytest.raises(ValidationError):
            validate_port("not-a-port")
        assert name == "csv-doctor"


class TestRegressionBehaviour:
    """Guards for previously-observed behaviour that must not change."""

    def test_stripping_whitespace_does_not_remove_inner_characters(self) -> None:
        with pytest.raises(ValidationError) as excinfo:
            validate_project_name("good bad")
        assert excinfo.value.code == "invalid_characters"

    def test_single_trailing_dot_domain_is_rejected(self) -> None:
        with pytest.raises(ValidationError) as excinfo:
            validate_email("user@example.org.")
        assert excinfo.value.code == "invalid_domain"

    def test_numeric_string_port_is_converted_to_int(self) -> None:
        result = validate_port("9999")
        assert result == 9999
        assert isinstance(result, int)

    def test_email_normalization_is_idempotent(self) -> None:
        first = validate_email("Dev@Example.ORG")
        assert validate_email(first) == first
