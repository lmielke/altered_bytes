from typing import Any, Dict

class PromptStats:
    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the class and variables for length tracking.
        """
        self.len_prompt = 0
        self.len_level_1 = {}

    def get_stats(self, *args, data_dict: Dict[Any, Any], **kwargs) -> Dict[Any, Any]:
        """
        Processes the dictionary and replaces values with their length, while tracking level 1 lengths.
        """
        result, _ = self._replace_with_length(0, *args, data_dict=data_dict, **kwargs)
        return result

    def _replace_with_length(self, level=0, *args, data_dict: Dict[Any, Any], **kwargs) -> (Dict[Any, Any], int):
        """
        Recursively processes the dictionary and replaces iterable values with their length.
        Non-iterable types (e.g., int, float) remain unchanged.
        
        Args:
            level: Current recursion level (0 for top-level).
            data_dict: The dictionary to process.

        Returns:
            A dictionary with values replaced by their lengths, and the total length at this level.
        """
        result = {}
        total_length = 0

        for key, value in data_dict.items():
            if isinstance(value, dict):
                # Recursively process nested dictionaries
                result[key], len_value = self._replace_with_length(level+1, *args, data_dict=value, **kwargs)
            elif value:
                # Replace the value with its length if it is an iterable
                len_value = len(str(value))
                result[key] = len_value
            else:
                len_value = 0
                result[key] = len_value

            total_length += len_value
            self.len_prompt += len_value

            if level == 1:
                self.len_level_1[key] = total_length
        print(f"\n{data_dict = }")
        print(f"\n{result = }")
        print(f"\n{total_length = }")
        return result, total_length
