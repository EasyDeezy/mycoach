from coach import Coach


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
