import re
from dataclasses import replace
from typing import Any, Iterator
from unittest.mock import patch

import pytest

import cercis
from tests.util import (
    DEFAULT_MODE,
    PY36_VERSIONS,
    all_data_cases,
    assert_format,
    dump_to_stderr,
    read_data,
)


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("cercis.dump_to_file", dump_to_stderr):
        yield


def check_file(
        subdir: str, filename: str, mode: cercis.Mode, *, data: bool = True
) -> None:
    source, expected = read_data(subdir, filename, data=data)
    assert_format(source, expected, mode, fast=False)


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
@pytest.mark.parametrize("filename", all_data_cases("simple_cases"))
def test_simple_format(filename: str) -> None:
    magic_trailing_comma = filename != "skip_magic_trailing_comma"
    check_file(
        "simple_cases", filename, cercis.Mode(magic_trailing_comma=magic_trailing_comma)
    )


@pytest.mark.parametrize("filename", all_data_cases("preview"))
def test_preview_format(filename: str) -> None:
    check_file("preview", filename, cercis.Mode(preview=True))


def test_preview_context_managers_targeting_py38() -> None:
    source, expected = read_data("preview_context_managers", "targeting_py38.py")
    mode = cercis.Mode(preview=True, target_versions={cercis.TargetVersion.PY38})
    assert_format(source, expected, mode, minimum_version=(3, 8))


def test_preview_context_managers_targeting_py39() -> None:
    source, expected = read_data("preview_context_managers", "targeting_py39.py")
    mode = cercis.Mode(preview=True, target_versions={cercis.TargetVersion.PY39})
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize(
    "filename", all_data_cases("preview_context_managers/auto_detect")
)
def test_preview_context_managers_auto_detect(filename: str) -> None:
    match = re.match(r"features_3_(\d+)", filename)
    assert match is not None, "Unexpected filename format: %s" % filename
    source, expected = read_data("preview_context_managers/auto_detect", filename)
    mode = cercis.Mode(preview=True)
    assert_format(source, expected, mode, minimum_version=(3, int(match.group(1))))


# =============== #
# Complex cases
# ============= #


def test_empty() -> None:
    source = expected = ""
    assert_format(source, expected)


@pytest.mark.parametrize("filename", all_data_cases("py_36"))
def test_python_36(filename: str) -> None:
    source, expected = read_data("py_36", filename)
    mode = cercis.Mode(target_versions=PY36_VERSIONS)
    assert_format(source, expected, mode, minimum_version=(3, 6))


@pytest.mark.parametrize("filename", all_data_cases("py_37"))
def test_python_37(filename: str) -> None:
    source, expected = read_data("py_37", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY37})
    assert_format(source, expected, mode, minimum_version=(3, 7))


@pytest.mark.parametrize("filename", all_data_cases("py_38"))
def test_python_38(filename: str) -> None:
    source, expected = read_data("py_38", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY38})
    assert_format(source, expected, mode, minimum_version=(3, 8))


@pytest.mark.parametrize("filename", all_data_cases("py_39"))
def test_python_39(filename: str) -> None:
    source, expected = read_data("py_39", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY39})
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY310})
    assert_format(source, expected, mode, minimum_version=(3, 10))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310_without_target_version(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = cercis.Mode()
    assert_format(source, expected, mode, minimum_version=(3, 10))


def test_patma_invalid() -> None:
    source, expected = read_data("miscellaneous", "pattern_matching_invalid")
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY310})
    with pytest.raises(cercis.parsing.InvalidInput) as exc_info:
        assert_format(source, expected, mode, minimum_version=(3, 10))

    exc_info.match("Cannot parse: 10:11")


@pytest.mark.parametrize("filename", all_data_cases("py_311"))
def test_python_311(filename: str) -> None:
    source, expected = read_data("py_311", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY311})
    assert_format(source, expected, mode, minimum_version=(3, 11))


@pytest.mark.parametrize("filename", all_data_cases("fast"))
def test_fast_cases(filename: str) -> None:
    source, expected = read_data("fast", filename)
    assert_format(source, expected, fast=True)


def test_python_2_hint() -> None:
    with pytest.raises(cercis.parsing.InvalidInput) as exc_info:
        assert_format("print 'daylily'", "print 'daylily'")
    exc_info.match(cercis.parsing.PY2_HINT)


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
def test_docstring_no_string_normalization() -> None:
    """Like test_docstring but with string normalization off."""
    source, expected = read_data("miscellaneous", "docstring_no_string_normalization")
    mode = replace(DEFAULT_MODE, string_normalization=False)
    assert_format(source, expected, mode)


def test_docstring_line_length_6() -> None:
    """Like test_docstring but with line length set to 6."""
    source, expected = read_data("miscellaneous", "linelength6")
    mode = cercis.Mode(line_length=6)
    assert_format(source, expected, mode)


def test_preview_docstring_no_string_normalization() -> None:
    """
    Like test_docstring but with string normalization off *and* the preview style
    enabled.
    """
    source, expected = read_data(
        "miscellaneous", "docstring_preview_no_string_normalization"
    )
    mode = replace(DEFAULT_MODE, string_normalization=False, preview=True)
    assert_format(source, expected, mode)


def test_long_strings_flag_disabled() -> None:
    """Tests for turning off the string processing logic."""
    source, expected = read_data("miscellaneous", "long_strings_flag_disabled")
    mode = replace(DEFAULT_MODE, experimental_string_processing=False)
    assert_format(source, expected, mode)


def test_stub() -> None:
    mode = replace(DEFAULT_MODE, is_pyi=True)
    source, expected = read_data("miscellaneous", "stub.pyi")
    assert_format(source, expected, mode)


def test_nested_class_stub() -> None:
    mode = replace(DEFAULT_MODE, is_pyi=True, preview=True)
    source, expected = read_data("miscellaneous", "nested_class_stub.pyi")
    assert_format(source, expected, mode)


def test_power_op_newline() -> None:
    # requires line_length=0
    source, expected = read_data("miscellaneous", "power_op_newline")
    assert_format(source, expected, mode=cercis.Mode(line_length=0))


def test_type_comment_syntax_error() -> None:
    """Test that cercis is able to format python code with type comment syntax errors."""
    source, expected = read_data("type_comments", "type_comment_syntax_error")
    assert_format(source, expected)
    cercis.assert_equivalent(source, expected)


@pytest.mark.parametrize(
    "filename, extra_indent",
    [
        ("func_def_extra_indent.py", True),
        ("func_def_no_extra_indent.py", False),
    ],
)
def test_function_definition_extra_indent(filename: str, extra_indent: bool) -> None:
    mode = replace(DEFAULT_MODE, function_definition_extra_indent=extra_indent)
    check_file("simple_cases", filename, mode)
