from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer
from torch import cuda

from allms.config import AppConfiguration
from .message import ChatMessage


class SingletonSentenceTransformer:
    """ Singleton class for sentence transformer """
    _instance: Optional[SentenceTransformer] = None

    @classmethod
    def get(cls, transformer_model: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
        if cls._instance is not None:
            return cls._instance

        def _load_model() -> SentenceTransformer:
            device = "gpu" if cuda.is_available() else "cpu"
            return SentenceTransformer(transformer_model, device=device)

        AppConfiguration.logger.log(f"Trying to load sentence transformer: {transformer_model} ...")
        cls._instance = _load_model()
        AppConfiguration.logger.log(f"Successfully loaded {transformer_model} ...")

        return cls._instance


class ChatHistoryDatabase:
    """ Class for the database storing the chats for long-term memory """
    def __init__(self, chat_name: str, rag_enabled: bool = False):
        self._chat_name = chat_name
        self._rag_enabled = rag_enabled
        self._initialized = False

        self._client: Optional[chromadb.Client] = None
        self._sentence_transformer: Optional[SentenceTransformer] = None
        self._collection: Optional[chromadb.Collection] = None

        self._message_ids: set[str] = set()  # Set of message IDs stored in the database

        self._metadata_key_timestamp = "timestamp"
        self._metadata_key_sent_by = "sent_by"
        self._metadata_key_sent_to = "sent_to"

    def is_initialized(self) -> bool:
        """ Returns True if database is initialized """
        return self._initialized

    async def initialize(self, enable_rag: bool = True) -> None:
        """ Initialize the database. Set enable_rag True if RAG is required """
        self._rag_enabled = enable_rag
        if self._rag_enabled:
            AppConfiguration.logger.log(f"RAG is enabled. Creating instance of chromadb and sentence transformer ...")
            self._client = chromadb.Client()
            self._sentence_transformer = SingletonSentenceTransformer.get()
            self._collection = self._client.create_collection(self._chat_name)
            self._initialized = True

    async def insert(self, messages: ChatMessage | list[ChatMessage]) -> None:
        """ Inserts the chat message(s) to the database """
        assert messages is not None, f"Expects a chat message but received None instead"
        if isinstance(messages, ChatMessage):
            messages = [messages]

        if not self._rag_enabled:
            return

        assert self._initialized, f"RAG is enabled but you forgot to initialize the database"

        msg_contents = [msg.msg for msg in messages]
        msg_ids = [msg.id for msg in messages]  # ID needs to be a string
        metadatas = [self.__create_metadata_from_message(msg) for msg in messages]
        msg_embeddings = self._sentence_transformer.encode(msg_contents)

        self._message_ids.update(msg_ids)
        AppConfiguration.logger.log(f"Inserting the following message IDs to the database: {msg_ids} ...")

        self._collection.add(
            embeddings=msg_embeddings,
            documents=msg_contents,
            metadatas=metadatas,
            ids=msg_ids
        )

    def retrieve_context(self, recent_msgs: list[ChatMessage], n_results: int = 10) -> list[str]:
        """ Retrieves the relevant messages from history based on the supplied query """
        fmt_msgs = [self.__format_message(msg.sent_by, msg.msg, msg.sent_to) for msg in recent_msgs]
        query = "\n".join(fmt_msgs)

        if not self._rag_enabled:
            return fmt_msgs

        query_embedding = self._sentence_transformer.encode(query)
        results = self._collection.query(query_embeddings=[query_embedding], n_results=n_results)

        # Note: Returns a 2D list due to support of batch queries
        metadatas = results["metadatas"][0]
        messages = results["documents"][0]
        results = []

        # Format the message before returning it
        # Formats it as "<agent> sent <message> to <sent-to> on <timestamp>"
        for msg, metadata in zip(messages, metadatas):
            timestamp = metadata[self._metadata_key_timestamp]
            sent_by = metadata[self._metadata_key_sent_by]
            sent_to = metadata[self._metadata_key_sent_to]

            fmt_msg = self.__format_message(sent_by, msg, sent_to, timestamp)
            results.append(fmt_msg)

        return results

    @staticmethod
    def __format_message(sent_by: str, msg_contents: str, sent_to: str = None, timestamp: str = None) -> str:
        """ Helper method to format the message  """
        # Formats it as "<agent> sent <message> to <sent-to> on <timestamp>"
        if sent_to is None:
            sent_to = "everyone"
        fmt_msg = f"{sent_by} sent '{msg_contents}' to {sent_to}"

        if timestamp is not None:
            fmt_msg = f"{fmt_msg} on {timestamp}"

        return fmt_msg

    def __create_metadata_from_message(self, message: ChatMessage) -> dict:
        """ Helper method to create a metadata from the message to add into the vector database """
        sent_to = message.sent_to
        if sent_to is None:
            sent_to = "everyone"  # Insertion will fail if the value is None

        metadata = {
            self._metadata_key_timestamp: message.timestamp,
            self._metadata_key_sent_by: message.sent_by,
            self._metadata_key_sent_to: sent_to
        }

        return metadata
