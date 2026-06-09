from abc import ABC, abstractmethod


class Interface_GmailIngestor(ABC):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def ingest_gmail(self, max_emails=10):
        pass

    @abstractmethod
    def fetch_message_ids(self, max_results=10):
        pass

    @abstractmethod
    def fetch_message(self, message_id, fmt="full"):
        pass