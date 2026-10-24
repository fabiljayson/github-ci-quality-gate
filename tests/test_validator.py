"""Happy-path tests for the quality_gate_demo validators."""

import pytest

from quality_gate_demo import (
    ValidationError,
    validate_email,
    validate_password,
    validate_port,
    validate_project_name,
)


class TestValidateProjectName:
    def test_accepts_simple_name(self) -> None:
        assert validate_project_name("csv-doctor") == "csv-doctor"

    def test_accepts_all_allowed_characters(self) -> None:
        name = "Ab_123-XYZ"
        assert validate_project_name(name) == name

    def test_strips_surrounding_whitespace(self) -> None:
        assert validate_project_name("  csv-doctor  ") == "csv-doctor"

    @pytest.mark.parametrize(
        ("name", "code"),
        [
            ("ab", "too_short"),
            ("x" * 65, "too_long"),
            ("my project", "invalid_characters"),
            ("bad/name", "invalid_characters"),
            ("çfirst", "invalid_characters"),
            ("admin", "reserved"),
            ("Root", "reserved"),
            ("NULL", "reserved"),
            ("", "empty"),
            ("   ", "empty"),
        ],
    )
    def test_rejects_with_expected_code(self, name: str, code: str) -> None:
        with pytest.raises(ValidationError) as excinfo:
            validate_project_name(name)
        assert excinfo.value.code == code
        assert excinfo.value.field == "name"


class TestValidatePort:
    def test_accepts_valid_int(self) -> None:
        assert validate_port(8080) == 8080

    def test_accepts_digit_string(self) -> None:
        assert validate_port("443") == 443

    def test_accepts_boundaries(self) -> None:
        assert validate_port(1) == 1
        assert validate_port(65535) == 65535

    @pytest.mark.parametrize(
        ("port", "code"),
        [
            (0, "out_of_range"),
            (65536, "out_of_range"),
            (-1, "out_of_range"),
            ("0", "out_of_range"),
            ("abc", "not_an_integer"),
            ("12.5", "not_an_integer"),
            ("", "not_an_integer"),
            ("-3", "not_an_integer"),
            (" 8080 ", "not_an_integer"),
            ("²", "not_an_integer"),
            (3.14, "unsupported_type"),
            (None, "unsupported_type"),
            (True, "unsupported_type"),
        ],
    )
    def test_rejects_with_expected_code(self, port: object, code: str) -> None:
        with pytest.raises(ValidationError) as excinfo:
            validate_port(port)  # type: ignore[arg-type]
        assert excinfo.value.code == code
        assert excinfo.value.field == "port"


class TestValidateEmail:
    def test_accepts_simple_address(self) -> None:
        assert validate_email("alice@example.org") == "alice@example.org"

    def test_lowercases_input(self) -> None:
        assert validate_email("  Alice@Example.ORG ") == "alice@example.org"

    def test_accepts_long_local_part_within_limit(self) -> None:
        addr = f"{'a' * 64}@example.org"
        assert validate_email(addr) == addr

    @pytest.mark.parametrize(
        ("email", "code"),
        [
            ("", "empty"),
            ("   ", "empty"),
            (None, "not_a_string"),
            (42, "not_a_string"),
            ("a" * 65 + "@example.org", "local_too_long"),
            ("x" * 255 + "@e.o", "too_long"),
            ("no-at-sign.org", "missing_at"),
            ("two@@example.org", "missing_at"),
            ("user@nodotdomain", "invalid_domain"),
            ("user@.example.org", "invalid_domain"),
            ("user@example.org.", "invalid_domain"),
            ("user@bad..domain.org", "invalid_domain"),
            ("@example.org", "empty_local"),
            ("a b@example.org", "contains_space"),
        ],
    )
    def test_rejects_with_expected_code(self, email: object, code: str) -> None:
        with pytest.raises(ValidationError) as excinfo:
            validate_email(email)  # type: ignore[arg-type]
        assert excinfo.value.code == code
        assert excinfo.value.field == "email"


class TestValidatePassword:
    def test_accepts_strong_password(self) -> None:
        assert validate_password("S3cure!Passw0rd") == "S3cure!Passw0rd"

    def test_accepts_exact_minimum_length(self) -> None:
        password = "Aa1!Aa1!Aa1!"
        assert len(password) == 12
        assert validate_password(password) == password

    @pytest.mark.parametrize(
        ("password", "code"),
        [
            (None, "not_a_string"),
            (1234, "not_a_string"),
            ("", "too_short"),
            ("Aa1!", "too_short"),
            ("Aa1!Aa1!Aa1", "too_short"),
            ("a1!a1!a1!a1!", "missing_category"),
            ("AA1!AA1!AA1!", "missing_category"),
            ("Aa!Aa!Aa!Aa!", "missing_category"),
            ("Aa1Aa1Aa1Aa1", "missing_category"),
        ],
    )
    def test_rejects_with_expected_code(self, password: object, code: str) -> None:
        with pytest.raises(ValidationError) as excinfo:
            validate_password(password)  # type: ignore[arg-type]
        assert excinfo.value.code == code
        assert excinfo.value.field == "password"

    def test_error_message_lists_all_missing_categories(self) -> None:
        # lowercase + uppercase present, digit and special missing.
        with pytest.raises(ValidationError) as excinfo:
            validate_password("aaaaaaaaaaaaA")
        message = str(excinfo.value)
        assert "digit" in message
        assert "special" in message
        assert "lowercase" not in message
        assert "uppercase" not in message
