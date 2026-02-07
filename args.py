import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Telegram Userbot")
    parser.add_argument("--clean-topics", action="store_true", help="Run the bad topics cleaner")
    parser.add_argument("--configure", action="store_true", help="Run the TUI configuration to select topics")
    return parser.parse_args()
