class BindingConfiguration:
    """ Class holding the global hotkey bindings """
    # Bindings for main screen
    main_show_about: str = "ctrl+a"

    # Bindings for modal screens
    modal_close_screen: str = "ctrl+w"

    # Bindings for new chat creation screen
    new_chat_randomize_scenario: str = "ctrl+r"
    new_chat_randomize_agent_persona: str = "ctrl+r"
    new_chat_customize_agents: str = "ctrl+s"
    new_chat_load_from_saved: str = "ctrl+l"

    # Bindings for chat screen
    chatroom_show_scenario: str = "f1"
    chatroom_show_your_persona: str = "f2"
    chatroom_show_all_persona: str = "f3"
    chatroom_modify_msgs: str = "f4"
    chatroom_start_vote: str = "f5"
    chatroom_send_message: str = "enter"
    chatroom_quit: str = "ctrl+w"

    # Bindings for modify message screen
    modify_msgs_mark_unmark_delete: str = "ctrl+x"
