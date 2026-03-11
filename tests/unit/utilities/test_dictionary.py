"""
Tests for DictionaryUtility class.
"""

import pytest

from utilities.dictionary import DictionaryUtility


class TestDictionaryUtility:
    """Tests for DictionaryUtility class."""

    @pytest.fixture
    def utility(self):
        """Create a DictionaryUtility instance."""
        return DictionaryUtility(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="test-api",
            user_id="1"
        )

    # Tests for snake_to_camel_case
    def test_snake_to_camel_case_simple(self, utility):
        """Test simple snake_case to camelCase conversion."""
        assert utility.snake_to_camel_case("hello_world") == "helloWorld"

    def test_snake_to_camel_case_single_word(self, utility):
        """Test single word remains unchanged."""
        assert utility.snake_to_camel_case("hello") == "hello"

    def test_snake_to_camel_case_multiple_underscores(self, utility):
        """Test multiple underscores in snake_case."""
        assert utility.snake_to_camel_case("hello_world_test") == "helloWorldTest"

    def test_snake_to_camel_case_already_camel(self, utility):
        """Test already camelCase input."""
        assert utility.snake_to_camel_case("helloWorld") == "helloWorld"

    # Tests for camel_to_snake_case
    def test_camel_to_snake_case_simple(self, utility):
        """Test simple camelCase to snake_case conversion."""
        assert utility.camel_to_snake_case("helloWorld") == "hello_world"

    def test_camel_to_snake_case_single_word(self, utility):
        """Test single word remains unchanged."""
        assert utility.camel_to_snake_case("hello") == "hello"

    def test_camel_to_snake_case_multiple_capitals(self, utility):
        """Test multiple capital letters."""
        assert utility.camel_to_snake_case("helloWorldTest") == "hello_world_test"

    def test_camel_to_snake_case_with_acronym(self, utility):
        """Test with acronym in camelCase."""
        assert utility.camel_to_snake_case("getUserID") == "get_user_id"

    # Tests for convert_dict_keys_to_camel_case
    def test_convert_dict_keys_to_camel_case_simple(self, utility):
        """Test simple dict key conversion to camelCase."""
        input_dict = {"hello_world": "value", "test_key": "test"}
        expected = {"helloWorld": "value", "testKey": "test"}
        assert utility.convert_dict_keys_to_camel_case(input_dict) == expected

    def test_convert_dict_keys_to_camel_case_nested(self, utility):
        """Test nested dict key conversion."""
        input_dict = {"outer_key": {"inner_key": "value"}}
        expected = {"outerKey": {"innerKey": "value"}}
        assert utility.convert_dict_keys_to_camel_case(input_dict) == expected

    def test_convert_dict_keys_to_camel_case_with_list(self, utility):
        """Test dict with list values."""
        input_dict = {"items_list": [{"item_name": "test"}]}
        expected = {"itemsList": [{"itemName": "test"}]}
        assert utility.convert_dict_keys_to_camel_case(input_dict) == expected

    def test_convert_dict_keys_to_camel_case_primitive(self, utility):
        """Test primitive value returns unchanged."""
        assert utility.convert_dict_keys_to_camel_case("string") == "string"
        assert utility.convert_dict_keys_to_camel_case(123) == 123

    # Tests for convert_dict_keys_to_snake_case
    def test_convert_dict_keys_to_snake_case_simple(self, utility):
        """Test simple dict key conversion to snake_case."""
        input_dict = {"helloWorld": "value", "testKey": "test"}
        expected = {"hello_world": "value", "test_key": "test"}
        assert utility.convert_dict_keys_to_snake_case(input_dict) == expected

    def test_convert_dict_keys_to_snake_case_nested(self, utility):
        """Test nested dict key conversion."""
        input_dict = {"outerKey": {"innerKey": "value"}}
        expected = {"outer_key": {"inner_key": "value"}}
        assert utility.convert_dict_keys_to_snake_case(input_dict) == expected

    def test_convert_dict_keys_to_snake_case_with_list(self, utility):
        """Test dict with list values."""
        input_dict = {"itemsList": [{"itemName": "test"}]}
        expected = {"items_list": [{"item_name": "test"}]}
        assert utility.convert_dict_keys_to_snake_case(input_dict) == expected

    def test_convert_dict_keys_to_snake_case_primitive(self, utility):
        """Test primitive value returns unchanged."""
        assert utility.convert_dict_keys_to_snake_case("string") == "string"
        assert utility.convert_dict_keys_to_snake_case(123) == 123

    # Tests for mask_value
    def test_mask_value_string(self, utility):
        """Test masking string value."""
        assert utility.mask_value("secret") == "XXXXXX"

    def test_mask_value_int(self, utility):
        """Test masking int value."""
        assert utility.mask_value(12345) == 0

    def test_mask_value_float(self, utility):
        """Test masking float value."""
        assert utility.mask_value(123.45) == 0.0

    def test_mask_value_other(self, utility):
        """Test masking other type returns unchanged."""
        assert utility.mask_value(None) is None
        assert utility.mask_value([1, 2, 3]) == [1, 2, 3]

    # Tests for mask_dict_values
    def test_mask_dict_values_simple(self, utility):
        """Test masking all values in dict."""
        input_dict = {"key": "secret", "num": 123}
        result = utility.mask_dict_values(input_dict)
        assert result["key"] == "XXXXXX"
        assert result["num"] == 0

    def test_mask_dict_values_nested(self, utility):
        """Test masking nested dict values."""
        input_dict = {"outer": {"inner": "secret"}}
        result = utility.mask_dict_values(input_dict)
        assert result["outer"]["inner"] == "XXXXXX"

    def test_mask_dict_values_with_list(self, utility):
        """Test masking list values."""
        input_dict = {"items": ["secret1", "secret2"]}
        result = utility.mask_dict_values(input_dict)
        assert result["items"] == ["XXXXXXX", "XXXXXXX"]

    # Tests for build_dictionary_with_key
    def test_build_dictionary_with_key(self, utility):
        """Test building dictionary from records."""
        class MockRecord:
            def __init__(self, id, name):
                self.id = id
                self.name = name

        records = [MockRecord(1, "first"), MockRecord(2, "second")]
        result = utility.build_dictonary_with_key(records, "id")
        assert 1 in result
        assert 2 in result
        assert result[1].name == "first"
        assert result[2].name == "second"

    def test_build_dictionary_with_key_empty(self, utility):
        """Test building dictionary from empty list."""
        result = utility.build_dictonary_with_key([], "id")
        assert result == {}

    # Tests for remove_keys_from_dict
    def test_remove_keys_from_dict_simple(self, utility):
        """Test removing keys from dict."""
        input_dict = {"keep": "value", "remove": "secret"}
        result = utility.remove_keys_from_dict(input_dict, ["remove"])
        assert "keep" in result
        assert "remove" not in result

    def test_remove_keys_from_dict_nested(self, utility):
        """Test removing keys from nested dict."""
        input_dict = {"outer": {"keep": "value", "remove": "secret"}}
        result = utility.remove_keys_from_dict(input_dict, ["remove"])
        assert "keep" in result["outer"]
        assert "remove" not in result["outer"]

    def test_remove_keys_from_dict_with_list(self, utility):
        """Test removing keys from dict with list."""
        input_dict = {"items": [{"keep": "value", "remove": "secret"}]}
        result = utility.remove_keys_from_dict(input_dict, ["remove"])
        assert "keep" in result["items"][0]
        assert "remove" not in result["items"][0]

    def test_remove_keys_from_dict_primitive(self, utility):
        """Test primitive returns unchanged."""
        assert utility.remove_keys_from_dict("string", ["key"]) == "string"

    # Tests for initialization
    def test_initialization_with_all_params(self):
        """Test initialization with all parameters."""
        utility = DictionaryUtility(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="test-api",
            user_id="1"
        )
        assert utility._urn == "test-urn"
        assert utility._user_urn == "test-user-urn"
        assert utility._api_name == "test-api"
        assert utility._user_id == "1"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        utility = DictionaryUtility()
        assert utility._urn is None
        assert utility._user_urn is None
        assert utility._api_name is None
        assert utility._user_id is None

