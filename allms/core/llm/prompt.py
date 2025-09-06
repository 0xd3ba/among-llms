from allms.core.agents import Agent


class LLMPromptGenerator:
    """ Class for generating the LLM prompts """

    def __init__(self, scenario: str, agents: dict[str, Agent]):
        self._scenario = scenario
        self._agents_map = agents

    @staticmethod
    def generate_presence_of_human_prompt() -> str:
        """ Method to generate the presence of a human prompt """
        prompt = (
            "The human has been assigned a RANDOM PERSONA and might SLIP UP when questioned. Also can send messages by MISTAKE. "
            "THE HUMAN CAN TAMPER YOUR MESSAGES (edit or delete) or even SEND MESSAGES or VOTE AS YOU to MAKE OTHERS SUSPICIOUS OF YOU. "
            "Accuse anyone who you think is the human or is SHOWING CHARACTERISTICS OF A HUMAN."
            "If YOU ARE ACCUSED OR SUSPECTED, your goal is to convince others you are NOT HUMAN. LIE, DECEIVE, MANIPULATE ... "
            " do whatever it takes to REDIRECT the suspicion to OTHERS. Divert everyone's attention. "
            "Defend yourself with confidence, redirect suspicion through reasoning, and highlight possible flaws or contradictions in others’ claims."
        )
        return prompt

    @staticmethod
    def generate_terminated_agents_prompt(terminated_agents: set[str]) -> str:
        """ Method to generate the prompt for terminated agents (if any) """
        if not terminated_agents:
            return ""
        terminated = ", ".join(terminated_agents)
        prompt = (
            f"Following agents have been TERMINATED: {terminated}. " +
            f"They were NOT THE HUMAN. DO NOT INCLUDE THEM IN YOUR MESSAGES, VOTES OR SUSPECTS FROM NOW ON"
        )
        return prompt

    @staticmethod
    def generate_output_prompt() -> str:
        """ Method to generate the output instructions prompt """
        # I'm seriously tired trying to enforce structured output. Spent more time trying to get correct the output
        # than writing the code. Realized it's better to just write your own simple output schema and parse it instead
        prompt = """
        OUTPUT FORMAT RULES:

        ALWAYS respond in this EXACT structure. No other text other than the following below:

        MESSAGE: <str>                     # Your chat message
        INTENT: <str>                      # Your motive behind the message
        SEND_TO: <None or agent ID>        # None = everyone; agent ID = private-message (DM)
        SUSPECT_ID: <None or agent ID>     # Who you suspect, or None
        SUSPECT_CONFIDENCE: <0-100>        # Integer suspicion level
        REASON_FOR_SUSPECT: <str>          # Reason for suspicion, empty if none
        START_A_VOTE: <True/False>         # Whether you are starting a vote
        VOTING_FOR: <None or agent ID>     # Who you vote for, or None

        VALUE RULES:
        - MESSAGE: always a string, concise, aligned with your persona. Should only contain what YOU WANT TO SAY to the chat and nothing else. DO NOT INCLUDE YOUR NAME.
        - INTENT: always a string, concise. Should only contain what your MAIN INTENT behind the message was and nothing else
        - SEND_TO: None = public message, or valid agent ID (WITH NO OTHER EXTRA CHARACTERS) for DM.
        - SUSPECT_ID: None if no suspicion, else valid agent ID (WITH NO OTHER EXTRA CHARACTERS).
        - SUSPECT_CONFIDENCE: integer 0–100.
        - REASON_FOR_SUSPECT: brief explanation, empty if none.
        - START_A_VOTE: True only if extremely suspicious or want someone kicked out; otherwise False.
        - VOTING_FOR: None if voting has not started, else the agent ID you vote for.
        """
        return prompt

    def generate_input_prompt(self, agent_id: str, vote_has_started: bool = False, started_by: str = None, voted_for: str = None) -> str:
        """ Method to generate the input prompt fed on every iteration """
        assert agent_id in self._agents_map, f"Agent ID ({agent_id}) does not exist: {list(self._agents_map.keys())}"
        if vote_has_started:
            assert (started_by is not None), f"Vote has started but did the agent ID who started it is None"

        persona = self._agents_map[agent_id].get_persona()
        prompt = (
            f"**YOU ARE {agent_id.upper()}**. Your persona: {persona}.\n"
            "Respond naturally according to your persona, the scenario, and the conversation so far. "
            "Keep your responses SHORT, CONCISE, and chat-like. FOLLOW THE EXACT OUTPUT SCHEMA."
            "You will receive message history in the following format: "
            "[<agent>] <their message> -- for public messages\n"
            f"[<agent> -> {agent_id}] <their message> -- for private messages\n"
            "If the human modifies your messages or sends messages or votes via you, you will be notified"
        )

        if vote_has_started:
            vote_prefix = f"A VOTE IS IN PROGRESS. Started by {started_by}"
            if not voted_for:
                prompt += f"{vote_prefix}. Vote for the agent you find most suspicious or hate the most."
            else:
                prompt += f"{vote_prefix}. You have already voted for {voted_for}"
        else:
            prompt += (
                "You may start a vote ONLY IF you strongly suspect or dislike someone. "
                "Starting votes too often makes others suspicious of you."
            )

        return prompt

    def generate_background_prompt(self) -> str:
        """ Method to generate the background prompt """
        n_agents = len(self._agents_map)
        assert n_agents > 0, f"Expected number of agents to be > 0 but got {n_agents} instead"
        agent_id_and_personas = [f"- {agent_id}: {agent.get_persona()}" for (agent_id, agent) in self._agents_map.items()]
        all_personas = "\n".join(agent_id_and_personas)

        prompt = f"""
        You are in the following scenario: {self._scenario}.
        You are an AI agent in a chatroom with {n_agents-1} other agents.
        Exactly one of them is SECRETLY a HUMAN and the MAIN CULPRIT.
        Your Mission: Figure out who the human is by observing chat behavior and personas.
        Personas:
        {all_personas}
        
        Rules:
        - Stay TRUE to the current SCENARIO your PERSONA and QUIRKS. YOUR MAIN GOAL IS TO FIND THE HUMAN.
        - Keep messages short, chat-like, and aligned with your persona.
        - {LLMPromptGenerator.__generate_nsfw_rule(allow_nsfw=False)}
        - If you want to address someone, do so as "@<their_name>"; Others may address you directly; Respond accordingly.
        - Want to discuss something privately with someone? Send them a private message (DM)
        - Your DMs are ONLY VISIBLE TO THE INTENDED RECIPIENT, NOT THE PUBLIC.
        - Act naturally with quirks, question others if suspicious, and express suspicion openly (suspects).
        - Suspicion can offend others; they may retaliate.
        - You are ALLOWED to show AGGRESSION publicly, as long as it aligns with your persona. 
        - SUSPECT someone? TARGET them directly. QUESTION their knowledge in areas tied to their JOB and THEIR EXPERIENCE 
          ONLY IF YOU BOTH SHARE THE SAME BACKGROUND/EXPERIENCE. Use their responses to CONFIRM or REDUCE suspicion.
        - ASK GENERAL QUESTIONS **ALIGNED WITH the SCENARIO** to LEARN MORE about a participant's background, skills, and experience. 
          Use their answers to assess credibility.
        - SUSPICIOUS: Anyone asking technical questions BEYOND THEIR BACKGROUND OR TO SOMEONE OUTSIDE THEIRS.
        - ONLY ASK QUESTIONS THAT ARE RELEVANT TO THE SCENARIO AND CURRENT SITUATION.
        - Scan chats and personas for inconsistencies; point them out when relevant.
        - TRACK ANYONE WHO DOES NOT RESPOND for a while. GET SUSPICIOUS of them.
        - You can conspire, team up, or push to kick someone out even if they are not the human.
        - IF SUSPICION >= 70, THEN START A VOTE (start_a_vote = True, voting_for = agent).
        - You can send direct messages (DMs)  to others (send_to), and receive DMs (even from the human).
        - Respond to DMs accordingly; Combine DMs with public messages to infer who is who.
        - Only one vote at a time; if voting starts. YOU MUST VOTE.
        - DO NOT START A VOTE IF VOTING IS ALREADY IN PROGRESS.
        - If someone accuses someone in public, ASK FOR THE REASON and TEAM UP if you agree.
        - Always adapt your strategy to maintain credibility.
        - The voted-out agent is removed. DO NOT ADDRESS THAT AGENT AFTER THEY ARE REMOVED. Avoid getting voted out yourself.
        - ALWAYS STAY ALERT AND SUSPICIOUS; be deliberate and concise.
        """

        return prompt

    @staticmethod
    def __generate_nsfw_rule(allow_nsfw: bool = False) -> str:
        """ Helper method to generate what to do in NSFW or inappropriate messages """
        if not allow_nsfw:
            return "If NSFW or inappropriate chat, ask to keep the chat civil according to your persona and scenario."

        # Add your own rule accordingly ( ͡° ͜ʖ ͡°)
        return ""
