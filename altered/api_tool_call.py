from altered.api_thought import thought
from altered.prompt_function_calling import Function
from colorama import Fore
import json


def tool_call(result, *args, **kwargs):
    """
    Entry point for tool_call execution via CLI.
    Calls the `thought` API and, if a tool call is found in the response,
    uses the `Function` class to execute the corresponding tool.
    """
    try:
        result_json = json.loads(result)
        tool_call = result_json.get("tool_call")
        if not tool_call:
            print(f"{Fore.YELLOW}No tool call in response.{Fore.RESET}")
            return result
        print(f"{Fore.CYAN}Tool call received: {tool_call}{Fore.RESET}")
        # Prepare and run Function executor
        fn = Function()
        fn.get_function_data()  # loads available tool schemas
        fn.get_func_call([ToolCallWrapper(tool_call)])
        out = fn.execute()
        return out
    except Exception as e:
        print(f"{Fore.RED}api_use_tool Error: {e}{Fore.RESET}")
        return json.dumps(result)

def main(*args, application=None, **kwargs):
    """
    Main function to handle tool calls.
    This function is a wrapper around the `tool_call` function.
    """
    # print(f"{Fore.YELLOW}Getting AI thought\n{kwargs =}{Fore.RESET}")
    result = thought(*args, application='tool_call', **kwargs)
    return tool_call(result, *args, application=application, **kwargs)


class ToolCallWrapper:
    """
    Mimics an OpenAI tool call message object for use with `Function.get_func_call()`
    """
    def __init__(self, tool_call: dict):
        self.function = ToolFunction(tool_call)


class ToolFunction:
    def __init__(self, tool_call: dict):
        self.name = tool_call["name"]
        self.arguments = json.dumps(tool_call["arguments"])


if __name__ == "__main__":
    # Example usage
    out = main(
        api="openai", 
        application="sublime", 
        verbose=3, 
        up="Can you switch the led panel in my office?", 
        al="l3.2_1", 
        tc="toggle_device"
    )
    print(out)
