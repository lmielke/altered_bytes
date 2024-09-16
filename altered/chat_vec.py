
from colorama import Fore, Style
from altered.data_vectorized import VecDB
from altered.thoughts import Chat
import altered.settings as sts


class VecChat(Chat):
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This overwirtes the simple data class from Chat with the VecDB version, which
        # can do vectorized search on the chat data
        self.data = VecDB(*args, **kwargs)
