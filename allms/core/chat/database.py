from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from .message import ChatMessage


class ChatHistoryDatabase:
    """ Class for the database storing the chats for long-term memory """
    def __init__(self, chat_name: str, transformer_model: str = "all-MiniLM-L6-v2"):
        self._chat_name = chat_name
        self._transformer_model = transformer_model

        self._client: Optional[chromadb.Client] = None
        self._sentence_transformer: Optional[SentenceTransformer] = None
        self._collection: Optional[chromadb.Collection] = None

        self._rag_enabled = True
        self._message_ids: set[str] = set()  # Set of message IDs stored in the database

        self._metadata_key_timestamp = "timestamp"
        self._metadata_key_sent_by = "sent_by"
        self._metadata_key_sent_to = "sent_to"

    def enable_rag(self, flag: bool = True) -> None:
        """ Set to True if RAG is required. By default, it's True """
        self._rag_enabled = flag
        if self._rag_enabled:
            self._client = chromadb.Client()
            self._sentence_transformer = SentenceTransformer(self._transformer_model)
            self._collection = self._client.create_collection(self._chat_name)

    def insert(self, messages: ChatMessage | list[ChatMessage]) -> None:
        """ Inserts the chat message(s) to the database """
        assert messages is not None, f"Expects a chat message but received None instead"
        if isinstance(messages, ChatMessage):
            messages = [messages]

        if not self._rag_enabled:
            return

        assert self._collection is not None, f"RAG is enabled but you forgot to instantiate chromadb.Collection"

        msg_contents = [msg.msg for msg in messages]
        msg_ids = [msg.id for msg in messages]  # ID needs to be a string
        metadatas = [self.__create_metadata_from_message(msg) for msg in messages]
        msg_embeddings = self._sentence_transformer.encode(msg_contents)

        self._message_ids.update(msg_ids)

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
