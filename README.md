# Jhon-bot

AI-powered VTuber assistant that reads Twitch chat, responds, and maintains lightweight conversational memory between streams. This repo currently ships Twitch chat logging and OpenAI integration, with a simple “memory checker” agent to curate past chat/context.

> **Status:** early prototype (logging + API scaffolding). Avatar/game control planned next.

---

##  Features

* **OpenAI integration** (Responses API): pluggable client ready to call models for generation.
* **Twitch chat grabber → JSONL logs**: connects to Twitch IRC over TLS and streams raw `PRIVMSG` lines to timestamped `.jsonl` files (one file per run/day).
* **Memory Checker agent (experimental):** curates historical context by selecting exactly 20 files from a set (via a safe `move_files` tool) for use next stream.

---

##  Requirements

* Python **3.10+**
* A valid **OpenAI API key**
* **Twitch IRC** credentials (OAuth token) and your channel handle
* `pip` for Python dependencies

---

##  Setup

1. **Clone & enter project**

   ```bash
   git clone <your-repo-url>
   cd Jhon-bot
   ```
2. **Create & activate venv (optional)**

   ```bash
   python -m venv .venv
   # Windows
   .venv\\Scripts\\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
3. **Install deps**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment**
   Create a `.env` in the project root:

   ```ini
   # OpenAI
   OAI=sk-...your_openai_key...

   # Twitch IRC
   SERVER=irc.chat.twitch.tv
   PORT=6697
   NICK=your_twitch_username
   TOKEN=oauth:your_twitch_oauth_token
   CHANNEL=yourchannel   # lower-case, no '#'
   ```

> The code uses `python-dotenv` to load variables. Ensure your `.env` is at the repo root.

---

##  Run the chat logger

This starts a TLS IRC connection, joins your channel, and writes all raw chat `PRIVMSG` lines to `logs/` in JSONL.

```bash
python Test.py
```

* On launch, a new file like `logs/twitch_chat_YYYYMMDD_HHMMSS.jsonl` is created.
* Each message is appended as a single JSON object per line.

### Log line format

```json
{"ts": 1726697973.123, "raw": ":user!user@user.tmi.twitch.tv PRIVMSG #yourchannel :hello world"}
```

> **Note:** function name is currently `twichchat_grabber` (without the second ‘t’). Keep imports consistent or rename carefully across files.

---

## Memory Checker (experimental)

`API_Setup.py` defines an agent named **“Memory Checker”**. It’s meant to:

* Inspect prior conversation/chat artifacts.
* Select **exactly 20** “most relevant” files to carry forward as next‑stream context.
* Use the `move_files` tool for safe file ops.

### The `move_files` tool (safe file mover/copier)

* **Contract:** no‑op unless **exactly 20** *unique, existing* paths are provided.
* Options: `do_copy` (default `True`) to copy instead of move, `overwrite` (default `False`).
* If a filename collision occurs and `overwrite=False`, a numeric suffix (`-1`, `-2`, …) is appended.
* Returns a JSON summary. Example success payload:

  ```json
  {
    "noop": false,
    "count": 20,
    "dest": "context_pool/",
    "moved": ["context_pool/file1.txt", "..."]
  }
  ```
* Example validation failure:

  ```json
  {
    "noop": true,
    "reason": "Requires exactly 20 unique, existing files.",
    "provided_count": 21,
    "unique_count": 21,
    "valid_count": 20,
    "missing": ["/path/that/does/not/exist.txt"]
  }
  ```

---

## How it works (high level)

* **OpenAI client:** constructed from `.env` key and ready for Responses API calls.
* **Twitch IRC:**

  * TLS socket → `PASS <oauth>`, `NICK <nick>`, `CAP REQ` for tags/commands/membership, `JOIN #<channel>`.
  * Responds to server `PING` with `PONG` to stay connected.
  * Streams only chat lines that contain `PRIVMSG` after successful join.
* **Logging:**

  * `Test.py` writes each raw line with a float timestamp to JSONL.
  * One file per run; filenames are time‑stamped to be unique.

---

## Quick verification checklist

* `.env` present and loaded (no missing vars).
* `TOKEN` is a valid Twitch IRC OAuth (format usually `oauth:...`).
* `CHANNEL` is all lower‑case and **without** the leading `#`.
* Port `6697` reachable. No firewall blocks.
* Observe a `:tmi.twitch.tv 001 <nick> :Welcome, GLHF!` line shortly after connect.

---

## Roadmap (suggested)

* [ ] Message parsing → structured fields (user, message, badges, etc.).
* [ ] Chat responder loop with rate limiting + safety filters.
* [ ] Basic memory store (vector DB / summaries) instead of raw file curation.
* [ ] Pluggable avatar/VTuber front‑end.
* [ ] Command system (`!help`, `!clip`, etc.).
* [ ] Unit tests + CI.

---

## Contributing

PRs are welcome! Please:

* Keep functions pure/testable where possible.
* Add docstrings and type hints.
* Update this README when changing public behavior.

---

## License

MIT (proposal). Update this section with your actual license choice.

---

## Acknowledgments

* Twitch IRC protocol and community docs.
* OpenAI developer ecosystem.
