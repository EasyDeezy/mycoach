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


def main():
    coach = Coach()
    print("MyCoach — type 'quit' to exit, 'reset' to start over.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
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
