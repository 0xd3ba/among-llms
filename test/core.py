# core.py -- Test whether the core chat-loop logic works or not

import asyncio
import logging

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.agents import Agent
from allms.core.chat import ChatMessageFormatter
from allms.core.state import GameStateManager

state_manager: GameStateManager = None
cancel_tasks = False

SCENARIO = "Currently on a spaceship headed to Mars"
PERSONAS = [
    "Driven and meticulous, she’s eager to be the first to confirm life beyond Earth. Often loses track of time in the lab, forgetting meals and sleep.",
    "Confident and charismatic, he enjoys the responsibility of guiding the ship. Has a habit of humming old Earth songs during long hours at the controls.",
    "Practical and hands-on, she treats the ship like her child. Known for her dry humor and for never leaving her toolkit behind.",
    "A former radio host, he’s sociable and upbeat, always keeping morale high. Runs a “daily space log” where he narrates the day’s events for both the crew and ground control."
]


async def on_message_update_callback(msg_id: str):
    """ Callback that is invoked on receiving a new message """
    msg = state_manager.get_message(msg_id)
    fmt_msg = ChatMessageFormatter.format_to_string(msg)
    msg_intent = msg.thought_process
    suspect = msg.suspect
    suspect_reason = msg.suspect_reason
    suspect_confidence = msg.suspect_confidence

    print(f"{fmt_msg} ({msg_intent})")
    print(f"\tSuspect: {suspect}\n\tConfidence: {suspect_confidence}\n\tReason: {suspect_reason}")
    print()


async def main(config: RunTimeConfiguration):
    global state_manager

    state_manager = GameStateManager(config)
    await state_manager.new()

    all_agents: dict[str, Agent] = state_manager.get_all_agents()
    all_agent_ids: list[str] = sorted(list(all_agents.keys()))

    # Overwrite the agents with the personas
    assert len(all_agents) == len(PERSONAS), f"No. of personas ({len(PERSONAS)}) != No. of agents ({len(all_agents)})"
    for persona, agent_id in zip(PERSONAS, all_agents.keys()):
        all_agents[agent_id].update_persona(persona)
        print(all_agents[agent_id])

    state_manager.update_scenario(SCENARIO)  # Overwrite the scenario
    state_manager.register_on_new_message_callback(on_message_update_callback)

    user_agent_id = all_agent_ids[0]
    state_manager.assign_agent_to_user(user_agent_id)
    logging.critical(f"You have been assigned the following agent: {state_manager.get_user_assigned_agent_id()}")

    # Start the loop!
    state_manager.start()

    while not cancel_tasks:
        await asyncio.sleep(1)

    state_manager.stop()


if __name__ == "__main__":
    rt_config = RunTimeConfiguration(
        ai_model="gpt-oss:20b",
        offline_model=True,
        ai_reasoning_lvl="medium",  # Parameter not used
        max_agent_count=len(PERSONAS),
        default_agent_count=len(PERSONAS),
        enable_rag=False,           # Parameter not used
        ui_dev_mode=False,          # Parameter not used
        skip_intro=False            # Parameter not used
    )

    try:
        asyncio.run(main(rt_config))
    except KeyboardInterrupt:
        logging.critical(f"Received keyboard interrupt -- cancelling the tasks")
        cancel_tasks = True
