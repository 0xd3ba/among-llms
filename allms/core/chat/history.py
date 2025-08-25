import asyncio
from collections import deque, OrderedDict
from dataclasses import dataclass, field

from allms.config import AppConfiguration
from .message import ChatMessage
from .database import ChatHistoryDatabase


@dataclass(frozen=True)
class ChatMessageHistory:
    """ Class for a storing the history of chat messages """
    enable_rag: bool = True   # Whether to enable Retrival Augmented Generation or not. Set to False if having performance issues

    # Maps message ID to the message for efficient retrieval and modification
    _history_all: OrderedDict[str, ChatMessage] = field(default_factory=OrderedDict)
    _global_database: ChatHistoryDatabase = field(default_factory=lambda: ChatHistoryDatabase("global_history"))
    # TODO: Maybe add a DM database for each agent as well ? Currently have no idea on how it might impact performance

    async def initialize(self) -> None:
        AppConfiguration.logger.log("Trying to initialize history database ...")
        await self._global_database.initialize(self.enable_rag)

    async def add(self, message: ChatMessage) -> None:
        """ Inserts the message into the history """
        msg_id = message.id
        assert not self.__has_message(msg_id), f"Can't insert as ID({msg_id}) of {message} already exists in the history"
        self._history_all[msg_id] = message

        AppConfiguration.logger.log(f"Request received to add message to history: {message}")
        # Insert to the global database only if the message is sent to everyone, i.e. sent_to is None
        # Also insert to the recent message IDs -- this will be the short-term context that will be provided to the agents
        sent_to = message.sent_to
        if sent_to is None:
            await self._global_database.insert(message)

    async def edit(self, msg_id: str, message: str, edited_by_you: bool = False) -> None:
        """ Edits the contents of the message in the history """
        assert self.__has_message(msg_id), f"Can't edit as ID({msg_id}) doesn't exist in the history"
        AppConfiguration.logger.log(f"Request received to edit message ID ({msg_id}) with '{message}', by_you={edited_by_you}")

        self._history_all[msg_id].edit(message, edited_by_you)

        # TODO: Edit the message in the database

    async def delete(self, msg_id: str, deleted_by_you: bool) -> None:
        """ Deletes the contents of the message from the history without removing the message """
        assert self.__has_message(msg_id), f"Can't delete as ID({msg_id}) doesn't exist in the history"
        AppConfiguration.logger.log(f"Request received to delete message ID ({msg_id}), by_you={deleted_by_you}")

        self._history_all[msg_id].delete(deleted_by_you)

        # TODO: Delete the message in the database

    def get(self, msg_id: str) -> ChatMessage:
        """ Returns the message from the history """
        assert self.__has_message(msg_id), f"Can't fetch as ID({msg_id}) doesn't exist in the history"
        return self._history_all[msg_id]

    def exists(self, msg_id: str) -> bool:
        """ Returns True if the message exists in the history, else False """
        return self.__has_message(msg_id)

    def __has_message(self, msg_id: str) -> bool:
        """ Helper method to check if a message exists in the history. Return True if exists """
        return msg_id in self._history_all
