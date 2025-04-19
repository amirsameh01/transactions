from abc import ABC, abstractmethod

class BaseMedium(ABC):
    @abstractmethod
    def send(self, message, recipient):
        pass

class SMSHandler(BaseMedium):
    def send(self, message, recipient):
        print(f"[SMS] Sending to {recipient}: {message}")

class EmailHandler(BaseMedium):
    def send(self, message, recipient):
        print(f"[EMAIL] Sending to {recipient}: {message}")
        return "some test"

class TelegramHandler(BaseMedium):
    def send(self, message, recipient):
        print(f"[TELEGRAM] Sending to {recipient}: {message}")

