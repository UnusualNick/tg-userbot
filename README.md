# Topic Silencer

*Zero-Inbox for the Telegram Power User.*

## The Problem

You join a high-value Supergroup for specific technical discussions. But the group also has a "General" or "Off-topic" thread that never stops moving.

Telegram has a flaw: **even if you mute that specific topic, the global unread counter for the group still goes up.**

This destroys the utility of your unread badges. Is that "1" notification a critical update in `#announcements`, or just another meme in `#random`? You never know until you check.

**Topic Silencer** fixes this by aggressively marking specific topics as read the moment a message arrives, keeping your unread counter meaningful.

## Features

- **Surgical Precision:** Only silences the specific topics you choose.
- **Live Monitoring:** Runs 24/7 to catch messages instantly.
- **One-Time Cleaner:** Can scrub your entire backlog in seconds.
- **TUI Configuration:** Easy-to-use terminal interface to select topics from your account.
- **Docker Ready:** Run it anywhere without Python dependency hell.

## Prerequisites

- **Telegram API Keys:** You need an `API_ID` and `API_HASH`.
  1. Login to [my.telegram.org](https://my.telegram.org/).
  2. Go to "API development tools".
  3. Copy your `app_id` and `api_hash`.

**For Docker Users:**
- Docker & Docker Compose installed.

**For Local Users:**
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip.

## Installation

### Option A: Docker Compose (Recommended)

This method requires zero local Python setup.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/tg-userbot.git
    cd tg-userbot
    ```

2.  **Setup Environment:**
    Create a `.env` file with your credentials:
    ```bash
    cp .env.example .env
    # Edit .env and add your API_ID and API_HASH
    ```

3.  **Prepare Session and Config Files:**
    Docker will create directories if these files don't exist, which will break the bot. Create empty files first:
    ```bash
    touch my_account.session
    echo "{}" > spammy_topics.json
    ```

4.  **First Run (Authentication):**
    Run interactively once to login to Telegram:
    ```bash
    docker compose run --rm userbot
    ```
    *Follow the prompts (enter phone number, code, 2FA password).*

5.  **Start Background Service:**
    Once authenticated, start the bot in the background:
    ```bash
    docker compose up -d
    ```

### Option B: Local Setup using uv

1.  **Sync Dependencies:**
    ```bash
    uv sync
    ```

2.  **Setup Environment:**
    Create `.env` and fill in your keys (same as above).

3.  **Run:**
    ```bash
    uv run python main.py
    ```

## Usage

### Live Monitoring (Default)
The bot monitors your chats in real-time. It silently marks message topics as read if they match your "spammy targets" list.
- **Docker:** `docker compose up -d`
- **Local:** `uv run python main.py`

### Configuration (TUI)
To select which topics to silence, run the text-based configuration tool.
- **Docker:** `docker compose run --rm userbot --configure`
- **Local:** `uv run python main.py --configure`
Use `Arrow Keys` to navigate and `Space` to toggle topics.

### One-Time Cleaner
To immediately clean existing unread counts without running the bot 24/7:
- **Docker:** `docker compose run --rm userbot --clean-topics`
- **Local:** `uv run python main.py --clean-topics`

## Disclaimer

This is a **Userbot**. It automates actions on your personal Telegram account.
- Use responsibly.
- While this bot only performs "Mark as Read" actions, Telegram's anti-spam systems are opaque.
- The author is not responsible for account bans or limitations.

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-new-feature`)
5. Create a new Pull Request
