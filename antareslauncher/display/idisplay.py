from abc import ABC, abstractmethod


class IDisplay(ABC):
    @abstractmethod
    def show_message(self, message, class_name, end="\n"):
        raise NotImplementedError

    @abstractmethod
    def show_error(self, string, class_name):
        raise NotImplementedError

    @abstractmethod
    def generate_progress_bar(self, iterator, desc, total=None):
        raise NotImplementedError
