## Customizing Keyboard Bindings
Among LLMs comes with intuitive, easy-to-remember keyboard bindings for navigating the interface. 
If you’d like to customize these bindings, you can do so by going to [`config/bindings.py`](../allms/config/bindings.py) 
and editing the `BindingConfiguration` class to your preference.  

```python
class BindingConfiguration:
    """ Class holding the global hotkey bindings """
    # Bindings for main screen
    main_show_about: str = "ctrl+a"                   # Opens up the about screen in main menu screen

    # Bindings for modal screens
    modal_close_screen: str = "ctrl+w"                # Closes any screen

    # Bindings for new chat creation screen
    new_chat_randomize_scenario: str = "ctrl+r"       # Randomizes the scenario from the selected genre
    new_chat_randomize_agent_persona: str = "ctrl+r"  # Randomizes the selected agent's persona
    new_chat_customize_agents: str = "ctrl+s"         # Shows the customize agents screen
    new_chat_load_from_saved: str = "ctrl+l"          # Shows the loading screen to use a saved state as a template

    # Bindings for chat screen
    chatroom_show_scenario: str = "f1"                # Shows the current scenario inside chatroom
    chatroom_show_your_persona: str = "f2"            # Shows who you have been assigned as, its persona and backstory
    chatroom_show_all_persona: str = "f3"             # Shows all the participants in the chatroom and their corresponding personas and backstories
    chatroom_modify_msgs: str = "f4"                  # Shows the screen that allows you to modify/delete messages
    chatroom_start_vote: str = "f5"                   # Shows the screen that allows you to vote
    chatroom_send_message: str = "enter"              # The key that is used to send a message
    chatroom_quit: str = "ctrl+w"                     # Closes the chatroom

    # Bindings for modify message screen
    modify_msgs_mark_unmark_delete: str = "ctrl+x"    # Marks the message for delete or removes the mark of deletion, in modify message screen
```

> [!TIP]  
> After updating a key binding, you may want to verify that it works. Before launching the application, set
> `ui_developer_mode: True` in [`config.yml`](../config.yml). 
> **This prevents the LLMs from starting when you enter the chatroom**, allowing you to test bindings freely.

> [!WARNING]
> Some key bindings are hardcoded in `textual`'s widgets by default. These cannot be overridden directly without modifying  
> the Among LLMs source code, which is outside the scope of this guide.
