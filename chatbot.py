
import random
import json
import os
import ast
import operator
from datetime import datetime

HISTORY_FILE = "chat_history.json"

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why was the computer cold? It left its Windows open!",
    "There are 10 types of people: those who understand binary and those who don't!"
]

RESPONSES = {
    "hello": ["Hello! Welcome to my chatbot.", "Hi there! How can I help?"],
    "how are you": ["I am doing great! Thanks for asking.", "All systems running smoothly!"],
    "your name": ["I am Advanced Python Chatbot."],
    "motivation": ["Keep learning. Small steps lead to big achievements!"],
    "study": ["Make a small plan, focus on one topic, and take short breaks."],
    "thank": ["You are welcome!", "Happy to help!"],
    "bye": ["Goodbye! Keep learning and coding!"]
}

# Safe calculator: supports only basic arithmetic
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

def calculate_node(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left = calculate_node(node.left)
        right = calculate_node(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")

        result = OPS[type(node.op)](left, right)

        if abs(result) > 1e100:
            raise ValueError("Result is too large.")

        return result

    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](calculate_node(node.operand))

    raise ValueError("Only basic arithmetic is allowed.")

def calculate(expression):
    tree = ast.parse(expression, mode="eval")
    return calculate_node(tree.body)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)
    except OSError:
        print("Bot: Unable to save chat history.")

def get_reply(message):
    text = message.lower().strip()

    if text in ("help", "commands"):
        return (
            "Available commands:\n"
            "- hello\n- how are you\n- your name\n"
            "- time\n- date\n- joke\n- motivation\n"
            "- study\n- calculate: 10 * (5 + 2)\n"
            "- history\n- clear history\n- bye"
        )

    if text == "time":
        return datetime.now().strftime("Current time: %I:%M %p")

    if text == "date":
        return datetime.now().strftime("Today's date: %d-%m-%Y")

    if text == "joke":
        return random.choice(JOKES)

    if text.startswith("calculate:"):
        expression = message.split(":", 1)[1].strip()
        try:
            if not expression:
                return "Please enter an expression, e.g. calculate: 10 + 5"
            result = calculate(expression)
            return f"Result: {result}"
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
            return "Invalid calculation. Try something like 10 + 5 * 2."

    for keyword, replies in RESPONSES.items():
        if keyword in text:
            return random.choice(replies)

    return "I don't know that yet. Type 'help' to see my commands."

def main():
    history = load_history()

    print("=" * 45)
    print("       ADVANCED PYTHON CHATBOT")
    print("=" * 45)
    print("Bot: Hello! Type 'help' to explore my features.")

    while True:
        try:
            message = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break

        if not message:
            print("Bot: Please enter a message.")
            continue

        if message.lower() == "history":
            if history:
                for item in history[-10:]:
                    print(f"{item['time']} | You: {item['user']}")
                    print(f"Bot: {item['bot']}")
            else:
                print("Bot: No saved conversations yet.")
            continue

        if message.lower() == "clear history":
            history.clear()
            save_history(history)
            print("Bot: Chat history cleared.")
            continue

        reply = get_reply(message)
        print("Bot:", reply)

        history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": message,
            "bot": reply
        })
        save_history(history)

        if message.lower() in ("bye", "exit", "quit"):
            break

if __name__ == "__main__":
    main()
