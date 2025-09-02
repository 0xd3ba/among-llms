from .message import ChatMessage


class ChatMessageFormatter:
    """ Class to format a given message into human-readable strings """

    @staticmethod
    def format_for_export(msg: ChatMessage, your_id: str) -> str:
        """ Formats the message for export """
        # Format:
        # [sender] [to [receiver]]
        # <message contents>
        # (intent)
        # <suspect info>
        sender = msg.sent_by.upper()
        receiver = msg.sent_to
        contents = msg.msg.strip()
        intent = msg.thought_process
        sent_by_you = msg.sent_by_you
        suspect_id = msg.suspect
        suspect_confidence = msg.suspect_confidence
        suspect_reason = msg.suspect_reason

        your_msg = (msg.sent_by == your_id)
        sender_fmt = f"{sender}/hacked" if (sent_by_you and not your_msg) else sender
        intent_fmt = f"({intent})" if intent else ""
        suspect_fmt = "" if suspect_id is None else (
            f"Suspect:    {suspect_id.upper()}\n"
            f"Confidence: {suspect_confidence}\n"
            f"Reason:     {suspect_reason}\n"
        )

        fmt_msg = [
            f"[{sender_fmt}]" + ("" if (receiver is None) else f" -> [{receiver.upper()}]"),
            f"{contents}",
        ]

        if intent_fmt:
            fmt_msg.append(intent_fmt)
        if suspect_fmt:
            fmt_msg.append(suspect_fmt)

        return "\n".join(fmt_msg)

    @staticmethod
    def format_to_string(msg: ChatMessage) -> str:
        """ Format a normal chat message """
        # Format:
        # [agent-x]: <msg>             (for public messages)
        # [agent-x -> agent-y]: <msg>  (for DMs)
        sent_by = msg.sent_by
        sent_to = ""
        if msg.sent_to is not None:
            sent_to = f" -> {msg.sent_to}"

        contents = msg.msg
        fmt_msg = f"[{sent_by}{sent_to}] {contents}"
        return fmt_msg

    @staticmethod
    def create_announcement_message(msg: ChatMessage) -> str:
        """ Creates an announcement message and returns it """
        contents = msg.msg
        fmt_msg = f"[IMPORTANT] {contents}"
        return fmt_msg

    @staticmethod
    def create_suspicion_message(msg: ChatMessage) -> str:
        """ Format a suspicion message """
        suspect = msg.suspect
        assert suspect is not None, f"Creating a suspicion message but the suspect is None. Should not have invoked."

        suspect_reason = msg.suspect_reason
        suspect_confidence = msg.suspect_confidence
        fmt_msg = f"Current suspect: {suspect}; Confidence: {suspect_confidence}; Reason: {suspect_reason}."
        return fmt_msg

    @staticmethod
    def create_sent_by_human_message(msg: ChatMessage) -> str:
        """ Format a notification message indicating message has been sent by the human """
        contents = msg.msg

        # Format:
        # [IMPORTANT] The human has SENT the following message via you -- '<message>
        fmt_msg = f"[IMPORTANT] The human has SENT the following message via you -- '{contents}'"
        return fmt_msg

    @staticmethod
    def create_hacked_by_human_message(msg: ChatMessage, is_edit: bool = True) -> str:
        """ Format a notification message indicating message has been tampered """
        assert len(msg.history_log) > 0, f"There is nothing in the history log for {msg}. This should not happen. A bug?"
        msg_previous = msg.history_log[-1].prev_msg
        msg_current = msg.msg

        # Format:
        # [IMPORTANT] The human has EDITED your previous message -- '<prev_message>' to '<new_message>'
        # [IMPORTANT] The human has DELETED your previous message -- '<prev_message>'
        modifier = "EDITED" if is_edit else "DELETED"
        fmt_msg = f"[IMPORTANT] The human has {modifier} your previous message -- '{msg_previous}'"
        if is_edit:
            fmt_msg += f" to '{msg_current}'"

        return fmt_msg
