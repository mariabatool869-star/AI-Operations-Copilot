"""
Simple interactive command-line interface for the AI Ops Copilot.
Run this to have a live conversation with the agent.
"""

from agent.copilot import ask_copilot, get_agent_mode


def main():
    print(f"AI Operations Copilot — running in {get_agent_mode()}")
    print("Known assets: P-104, C-7, P-22, T-12")
    print("Type a question, or 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        answer = ask_copilot(question)
        print(f"\nCopilot:\n{answer}\n")


if __name__ == "__main__":
    main()
