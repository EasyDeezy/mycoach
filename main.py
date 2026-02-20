import os
import subprocess
from coach import Coach

# Load ANTHROPIC_API_KEY from ~/.zshrc if not already set
if not os.environ.get("ANTHROPIC_API_KEY"):
    result = subprocess.run(
        ["zsh", "-c", "source ~/.zshrc && echo $ANTHROPIC_API_KEY"],
        capture_output=True, text=True
    )
    key = result.stdout.strip()
    if key:
        os.environ["ANTHROPIC_API_KEY"] = key


def strip_markdown(text: str) -> str:
    import re
    text = re.sub(r"#{1,6}\s*", "", text)       # headings
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text) # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)      # italic
    text = re.sub(r"`(.+?)`", r"\1", text)         # inline code
    text = re.sub(r"^[-*]\s+", "- ", text, flags=re.MULTILINE)  # bullets
    text = re.sub(r"\n{3,}", "\n\n", text)         # excess blank lines
    return text.strip()


def save_conversation(history: list) -> None:
    path = "/tmp/mycoach_conversation.txt"
    with open(path, "w") as f:
        f.write("MyCoach Conversation\n")
        f.write("=" * 40 + "\n\n")
        for msg in history:
            role = "You" if msg["role"] == "user" else "Coach"
            content = strip_markdown(msg["content"])
            f.write(f"{role}: {content}\n\n")
    print(f"\nConversation saved to {path} — print with: lpr {path}")


def main():
    coach = Coach()
    print("MyCoach — type 'quit' to exit, 'reset' to start over.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            save_conversation(coach.history)
            break
        if user_input.lower() == "reset":
            coach.reset()
            print("Conversation reset.\n")
            continue

        print("Coach: ", end="", flush=True)
        coach.chat(user_input)
        print()


if __name__ == "__main__":
    main()
