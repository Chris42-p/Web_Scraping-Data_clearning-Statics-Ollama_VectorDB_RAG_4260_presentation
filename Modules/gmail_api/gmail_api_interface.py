from abc import ABC, abstractmethod

class Interface_GmailIngestor(ABC):
    @abstractmethod
    def build_auth_url(self, state: str) -> tuple[str, str]:
        pass

    @abstractmethod
    def exchange_code_for_tokens(self, code: str, state: str) -> dict:
        pass

    @abstractmethod
    def set_credentials_from_token_info(self, token_info: dict) -> None:
        pass

    @abstractmethod
    def fetch_message_ids(self, max_results: int = 10) -> list:
        pass

    @abstractmethod
    def fetch_message(self, message_id: str, fmt: str = "full") -> dict:
        pass

    @abstractmethod
    def ingest_gmail(self, max_emails: int = 10) -> list:
        pass