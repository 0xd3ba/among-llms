from dataclasses import dataclass, field
from typing import Optional

from allms.config import AppConfiguration


@dataclass
class ChatMessageEditLog:
    """ Class for edit-log of a chat message """
    timestamp: str
    prev_msg: str
    edited_by_you: bool
    deleted_by_you: bool


@dataclass
class ChatMessage:
    """ Class for a single chat message """
    id: str                            # The unique identifier of the message
    timestamp: str                     # Timestamp in ISO format (YYYY-MM-DD HH:MM:SS) when the message was sent
    msg: str                           # The contents of the message
    sent_by: str                       # The originator of the message (can be you or a LLM)
    sent_by_you: bool                  # Set to true if it was YOU who sent the message

    sent_to: Optional[str] = None      # The recipient of the message (can be everyone (None) or a single agent)
    thought_process: str = ""          # The thought process behind the message (only set by the LLMs)
    reply_to_id: Optional[str] = None  # If the message is a reply to a previous message
    edited: bool = False               # Set to true if the message was edited (either by you or the LLM)
    deleted: bool = False              # Set to true if the message was deleted (either by you or the LLM)
    edited_by_you: bool = False        # Set to true if it was YOU who edited the message
    deleted_by_you: bool = False       # Set to true if it was YOU who deleted the message

    # Only set by the LLMs if they suspect anybody
    suspect: Optional[str] = None             # Agent ID of the current suspect while this message was sent
    suspect_confidence: Optional[int] = None  # A score between [0, 100] range describing the confidence
    suspect_reason: Optional[str] = None      # The reason behind suspecting the agent

    # Stores the history of the edits/delete of the message
    history_log: list[ChatMessageEditLog] = field(default_factory=list)

    def can_edit_or_delete(self) -> bool:
        """ Returns True if allowed to edit/delete, else False """
        return not self.deleted

    def edit(self, message: str, edited_by_you: bool) -> None:
        """ Edits the message with the new contents """
        if not self.can_edit_or_delete():
            return

        prev_msg = self.msg
        self.msg = message
        self.edited = True
        self.edited_by_you = edited_by_you

        curr_ts = AppConfiguration.clock.current_timestamp_in_iso_format()
        edit_log = ChatMessageEditLog(timestamp=curr_ts, prev_msg=prev_msg, edited_by_you=edited_by_you, deleted_by_you=False)
        self.history_log.append(edit_log)

    def delete(self, deleted_by_you: bool) -> None:
        """ Deletes the message and updates the latest contents """
        if not self.can_edit_or_delete():
            return

        prev_msg = self.msg
        self.deleted = True
        self.deleted_by_you = deleted_by_you
        self.msg = "This message has been deleted"

        curr_ts = AppConfiguration.clock.current_timestamp_in_iso_format()
        edit_log = ChatMessageEditLog(timestamp=curr_ts, prev_msg=prev_msg, edited_by_you=False, deleted_by_you=deleted_by_you)
        self.history_log.append(edit_log)
        # Note: No longer edits or delete possible on this message from now on
