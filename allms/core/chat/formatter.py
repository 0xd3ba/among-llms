from .message import ChatMessage


class ChatMessageFormatter:
    """ Class to format a given message into human-readable strings """

    @staticmethod
    def format_to_string(msg: ChatMessage) -> str:
        """ Format a normal chat message """
        # Format:
        # [timestamp][agent-x]: <msg>             (for public messages)
        # [timestamp][agent-x -> agent-y]: <msg>  (for DMs)
        timestamp = msg.timestamp
        sent_by = msg.sent_by
        sent_to = ""
        if msg.sent_to is not None:
            sent_to = f" -> {msg.sent_to}"

        contents = msg.msg
        fmt_msg = f"[{timestamp}][{sent_by}{sent_to}] {contents}"
        return fmt_msg

    @staticmethod
    def create_sent_by_human_message(msg: ChatMessage) -> str:
        """ Format a notification message indicating message has been sent by the human """
        timestamp = msg.timestamp
        contents = msg.msg

        # Format:
        # [timestamp][IMPORTANT] The human has SENT the following message via you -- '<message>
        fmt_msg = f"[{timestamp}][IMPORTANT] The human has SENT the following message via you -- '{contents}'"
        return fmt_msg

    @staticmethod
    def create_hacked_by_human_message(msg: ChatMessage, is_edit: bool = True) -> str:
        """ Format a notification message indicating message has been tampered """
        assert len(msg.history_log) > 0, f"There is nothing in the history log for {msg}. This should not happen. A bug?"
        msg_previous = msg.history_log[-1].prev_msg
        msg_current = msg.msg
        modify_timestamp = msg.history_log[-1].timestamp

        # Format:
        # [timestamp][IMPORTANT] The human has EDITED your previous message -- '<prev_message>' to '<new_message>'
        # [timestamp][IMPORTANT] The human has DELETED your previous message -- '<prev_message>'
        modifier = "EDITED" if is_edit else "DELETED"
        fmt_msg = f"[{modify_timestamp}][IMPORTANT] The human has {modifier} your previous message -- '{msg_previous}'"
        if is_edit:
            fmt_msg += f" to '{msg_current}'"

        return fmt_msg
