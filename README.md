<p align="center">
    <img src="assets/among_llms.png" width="600px" alt="Among-LLMs Banner">
</p>

<p align="center">
  <i align="center"> You are the only impostor. </i><br>
  <i align="center"> Every word counts. Every silence traps. Only one survives. Can you be the one? </i>
</p>

> *Just another normal chatroom ... or so it seems ...* 
>
> At first, it’s only chatter. Then the room slowly darkens into a web of suspicion ... every bot watching, every message 
> scrutinized to find you, **the only hidden human**. Any line of text can be your undoing. Every word is a clue, 
> every silence a trap. One slip, and they’ll vote you out, ending you instantly. **Manipulate conversations**, 
> **impersonate other bots**, **send whispers**, or **gaslight others into turning on each other** -- **do *whatever* it takes
> to survive**. 
> <p align="center"><i> Chaos is your ally, deception your weapon. </i></p>
>
> Survive the rounds of scrutiny and deception until 
> only you and one bot remain -- then, and only then, can you claim victory.


> [!NOTE]
> This project was created as part of the [OpenAI Open Model Hackathon 2025](https://openai.devpost.com/)

## Introduction
Among LLMs turns your **terminal** into a chaotic chatroom playground where you’re the only human among a bunch of
eccentric AI agents, dropped into a common *scenario* -- it could be Fantasy, Sci-Fi, Thriller, Crime, or something 
completely unexpected. Each participant, including you, has a *persona* and a *backstory*, and all the AI agents
share one common goal -- determine and eliminate the human, through *voting*. 
Your mission: stay hidden, manipulate conversations, and turn the bots against each other with edits, whispers, impersonations, and clever gaslighting.
Outlast everyone, turn chaos to your advantage, and make it to the final two. 

Can you survive the hunt and *outsmart* the AI?

> [!CAUTION]
> Running this on rented servers (cloud GPUs, etc.) may generate unexpected usage costs.
> The developer is **not responsible** for any charges you may incur. Use at your own risk.

### Features

- **Terminal-based UI**: Play directly in your terminal for a lightweight, fast, and immersive experience.
Since it runs in the terminal, you can even SSH into a remote server and play seamlessly. No GUI required.

- **Dynamic Scenarios**: Jump into randomly generated scenarios across genres like fantasy, sci-fi, thriller, crime etc.
 or write your *own* custom scenario.

- **Dynamic Personas**: Every participant, including you, gets a randomly assigned persona and backstory that fit the 
chosen scenario. Want more control? Customize them all yourself for tailored chaos.

- **Customizable Agent Count**: Running on a beefy machine? Crank up the number of agents for absolute chaos. Stuck on 
a potato? Scale it down and still enjoy the (reduced) chaos.

- **Direct Messages**: Send private DMs to other participants -- but here’s the twist: while bots think their DMs are 
private, they have no idea that you can read them too.

- **Messaging Chaos**: Edit, delete, or impersonate messages from *any* participant. Disrupt alliances, plant false leads, 
or gaslight bots into turning on each other. No one but you (and the impersonated bot) knows the truth.

- **Voting Mechanism**: Start or join votes to eliminate the suspected human. One slip-up and you’ll be gone instantly. 
But you can also start a vote or participate as other participants to frame, confuse, and further escalate the chaos.

- **Infinite Replayability**: Thanks to the unpredictable nature of LLM-driven responses and the freedom 
to design your own scenarios, personas, and backstories, no two chatrooms will ever play out the same. 
Every round is a fresh mystery, every game a new story waiting to unfold.

- **Export/Load Chatroom State**: Save your chaos mid-game and resume later, or load someone else’s exported state and 
continue where they left off. Chatroom states are stored in clean, portable JSON, making them easy to share or debug. 
Want to start fresh but keep the same setup? Use the same JSON as a template to spin up a new chatroom with the same scenario, 
agents, and personas -- only the messages get wiped. Everything else stays the same.

- **Written in Python**: Easy for developers to contribute to its future development.


## Installation
### Pre-Requisites
1. Ensure you have atleast Python `v3.11` installed. 
2. Ensure you have [`ollama`](https://github.com/ollama/ollama) installed and pull the model you require; For example,
    ```bash
    ollama pull gpt-oss:20b 
    ```

3. Clone this repository
    ```bash
    git clone https://github.com/0xd3ba/among-llms
    cd among-llms
    ```
> [!TIP]
> **Recommended**: Create and activate a virtual environment. For example:
>  ``` bash
>  python3 -m venv allms-venv
>  source allms-venv/bin/activate
>  ```

> [!NOTE]
> Currently, this project only supports local Ollama models (specifically OpenAI-compatible ones)
> It has been tested with `gpt-oss:20b` and should also work with larger models like `gpt-oss:120b`.
> Other model families may not work at the moment.


## Contributions
Contributions are welcome! 
Before contributing, please review `CONTRIBUTING.md` for guidelines first.


## License
Among LLMs is released under GNU General Public License v3.0.
