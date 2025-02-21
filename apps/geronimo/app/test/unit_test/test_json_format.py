import pytest
import sys
import os

# Add the app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utils.json_format import format_json_string


@pytest.mark.parametrize(
    "input_string, expected_output",
    [
        #  Test case : 1 Valid JSON string
        ('{"name": "Alice", "age": 30}', {"name": "Alice", "age": 30}),
        #  Test case : 2 Invalid JSON string
        ("{name: Alice, age: 30}", None),
        #  Test case : 3 String containing multiple valid JSON objects
        (
            'Some text before ```json{"name": "Alice"}``` and another ```json{"age": 30}``` some text after',
            [{"name": "Alice"}, {"age": 30}],
        ),
        #  Test case : 4 Partial JSON-like content that cannot be extracted
        ("Random text {name: Alice, age: 30} more text", None),
        #  Test case : 5 Empty string should return None
        ("", None),
        #  Test case : 6 Whitespace string should return None
        ("     ", None),
        # Test case : 7 Single valid JSON object inside extra text
        (
            'Here is some text {"city": "New York"} and more text',
            [{"city": "New York"}],
        ),
        #  Test case :8 Multiple JSON objects with extra spaces
        (
            '  {"key": "value"} some junk {"another": 42}   ',
            [{"key": "value"}, {"another": 42}],
        ),
        #  Test case :9 Incorrect JSON format with missing brackets
        ("Just a string with {wrong json", None),
    ],
)
def test_format_json_string(input_string, expected_output):
    """Test format_json_string function with different inputs."""
    result = format_json_string(input_string)
    assert result == expected_output
