# main.py
from llm import start_sales_conversation, get_ai_response
from cartesia_tts import speak

def main():
    # Initialize the LLM conversation
    conversation_history = start_sales_conversation()

    print("AI Sales Agent: Hello! My name is Ravi. May I have your first and last name, please?")
    speak("Hello! My name is Ravi. May I have your first and last name, please?")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            goodbye_message = "Thank you for your time. Have a great day!"
            print(f"AI Sales Agent: {goodbye_message}")
            speak(goodbye_message)
            break

        # Get AI response from llm.py
        ai_reply, conversation_history = get_ai_response(user_input, conversation_history)

        # Print and speak the AI response
        speak(ai_reply)

if __name__ == "__main__":
    main()