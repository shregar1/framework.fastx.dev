"""
Utility class for dictionary and key transformation operations, including
camel/snake case conversion and masking.
"""
import re

from abstractions.utility import IUtility


class DictionaryUtility(IUtility):
    """
    Utility for dictionary manipulation, key conversion,
    and masking operations.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self._urn: str = urn
        self._user_urn: str = user_urn
        self._api_name: str = api_name
        self._user_id: str = user_id
        self.logger.debug(
            f"DictionaryUtility initialized for "
            f"user_id={user_id}, urn={urn}, api_name={api_name}"
        )

    def build_dictonary_with_key(self, records: list, key: str):
        """
        Build a dictionary from a list of records using a specified attribute
        as the key.
        Args:
            records (List): List of objects.
            key (str): Attribute name to use as the key.
        Returns:
            dict: Dictionary mapping key values to records.
        """
        self.logger.info(f"Building dictionary with key: {key}")

        result: dict = {}

        for record in records:
            result[getattr(record, key)] = record

        return result

    def snake_to_camel_case(self, snake_str):
        """
        Convert a snake_case string to camelCase.
        Args:
            snake_str (str): The snake_case string.
        Returns:
            str: The camelCase version of the string.
        """
        self.logger.debug(f"Converting snake_case to camelCase: {snake_str}")
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    def convert_dict_keys_to_camel_case(self, data):
        """
        Recursively convert all dictionary keys from snake_case to camelCase.
        Args:
            data (dict or list): The data structure to convert.
        Returns:
            dict or list: Data with keys converted to camelCase.
        """
        self.logger.debug("Converting dictionary keys to camelCase")
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                new_key = self.snake_to_camel_case(k)
                new_dict[new_key] = self.convert_dict_keys_to_camel_case(v)
            return new_dict
        elif isinstance(data, list):
            return [
                self.convert_dict_keys_to_camel_case(item) for item in data
            ]
        else:
            return data

    def camel_to_snake_case(self, name: str) -> str:
        """
        Convert a camelCase string to snake_case.
        Args:
            name (str): The camelCase string.
        Returns:
            str: The snake_case version of the string.
        """
        self.logger.debug(f"Converting camelCase to snake_case: {name}")
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def convert_dict_keys_to_snake_case(self, data: dict):
        """
        Recursively convert all dictionary keys from camelCase to snake_case.
        Args:
            data (dict or list): The data structure to convert.
        Returns:
            dict or list: Data with keys converted to snake_case.
        """
        self.logger.debug("Converting dictionary keys to snake_case")

        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                new_key = self.camel_to_snake_case(k)
                new_dict[new_key] = self.convert_dict_keys_to_snake_case(v)
            return new_dict

        elif isinstance(data, list):

            return [
                self.convert_dict_keys_to_snake_case(item) for item in data
            ]

        else:
            return data

    def mask_value(self, value):
        """
        Mask a value for privacy (e.g., replace with 'X' or zero).
        Args:
            value (str, int, float): The value to mask.
        Returns:
            Masked value of the same type.
        """
        self.logger.debug(f"Masking value: {value}")
        if isinstance(value, str):
            return "X" * len(value)
        elif isinstance(value, int):
            return 0
        elif isinstance(value, float):
            return 0.0
        return value

    def mask_dict_values(self, data):
        """
        Recursively mask all values in a dictionary or list.
        Args:
            data (dict or list): The data structure to mask.
        Returns:
            dict or list: Data with all values masked.
        """
        self.logger.debug("Masking dictionary values")
        if isinstance(data, dict):
            return {k: self.mask_dict_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.mask_dict_values(item) for item in data]
        else:
            return self.mask_value(data)

    def remove_keys_from_dict(
        self, data: dict, keys_to_remove: list[str]
    ) -> dict:
        """
        Remove specified keys from a dictionary recursively.
        Args:
            data (dict): Dictionary from which keys need to be removed.
            keys_to_remove (List[str]): List of keys to remove.
        Returns:
            dict: Dictionary with specified keys removed.
        """
        self.logger.info(f"Removing keys from dict: {keys_to_remove}")
        if isinstance(data, dict):
            return {
                k: self.remove_keys_from_dict(v, keys_to_remove)
                for k, v in data.items()
                if k not in keys_to_remove
            }
        elif isinstance(data, list):
            return [
                self.remove_keys_from_dict(i, keys_to_remove) for i in data
            ]
        else:
            return data
