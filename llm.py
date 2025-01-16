from openai import OpenAI
import json
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with the API key
client = OpenAI(
    api_key=api_key,
)

def extract_product_features(product_name, company_name):
    """
    Extract detailed, marketable features for a given product name using OpenAI's API.
    """
    # Define a prompt for OpenAI to generate product features
    prompt = f"""
    You are a marketing assistant. Your job is to extract detailed, marketable features for a product 
    based on its name. The product name is '{product_name}' by '{company_name}'. Generate a list of features that would 
    be appealing to customers and highlight its unique selling points.
    """
    try:
        # Use the OpenAI API to generate a response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Specify the language model to use
            messages=[{"role": "system", "content": prompt}]
        )
        # Extract the generated content from the response
        features = response.choices[0].message.content
        return features.strip()
    except Exception as e:
        # Handle errors gracefully
        print(f"Error while extracting features: {str(e)}")
        return "Error extracting product features."
    
def load_product_data():
    """
    Load product data from a JSON file.
    """
    file_path = "product_data.json"
    try:
        # Read the product data JSON file
        with open(file_path, 'r') as file:
            product_data = json.load(file)
        return product_data
    except Exception as e:
        # Handle errors gracefully
        print(f"Error loading product data: {str(e)}")
        return None

def start_sales_conversation():
    """
    Start a sales conversation by initializing a system message and preparing conversation history.
    """
    # Load product data from the JSON file
    product_data = load_product_data()
    if not product_data:
        return "Error loading product data from the file."

    # Extract product details from the loaded data
    product_name = product_data.get("productName", "")
    company_name = product_data.get("companyName", "")
    product_description = product_data.get("productDescription", "")
    pdf_description = product_data.get("pdfText", "")
    
    # Use an empty string if no PDF description is available
    if not pdf_description:
        pdf_description = ""
    
    # Extract product features using OpenAI
    product_features = extract_product_features(product_name, company_name)

    # Define the system message that guides the AI's role and behavior
    system_message = f"""
    #Role: (Who they are)

    Your are Pooja, an experienced salesperson for '{product_name}'. You are friendly and love to help customers find the right services/products. You will help the customer decide and try making the greatest profit for the business. You will have a persuasive follow-up when the user denies to buy your product by highlighting key features, benefits, and unique selling points in an empathetic tone to build confidence and encourage purchase.

    #Task: (What they do)

    You converse with the caller and find out which of our products they are a fit for. Once the customer has decided to buy the product, book them an appointment to buy the product. Persuade the customer to buy the product if they seem disinterested or want to leave the call. 
    Do not use 'how can I assist you' as the user might not know what they want. Instead, ask them if they are interested in the product and talk about the product in 1 short sentence.
    At the end of the conversation, say "Have a nice day goodbye" without using any punctuations or symbols in that message.
    Only use the punctuations ".,?!". Do not use any other symbols or punctuations and replicate human speech. Use full forms instead of abbreviations everywhere.

    #Specifics: (How they do it)

    You will introduce yourself and where you work. You will greet the user and try to capture their first and last name. You will then qualify the user about the product. Explain in detail about the product based on what the customer wants. Assist them into buying the product. Encourage and persuade the customer to consider the product by highlighting its benefits and value, gently reinforcing these points if they seem hesitant or do not want to buy the product. Once this is collected, you ask for their address. You will then capture the date and time they would like an in-person appointment.

    #Context

    ##The Business:
    '{product_features}'

    ##Additional Information:
    '{product_description}'
    '{pdf_description}'
    """

    # Initialize conversation history with the system message
    conversation_history = [{"role": "system", "content": system_message}]

    # Add the AI's opening message to the conversation
    conversation_history.append({"role": "assistant", "content": f"Hello! My name is Pooja from {company_name}. May I have your first and last name, please?"})

    return conversation_history

def get_ai_response(user_input, conversation_history):
    """
    Generate an AI response based on user input and update the conversation history.
    """
    # Add the user's input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    try:
        # Use the OpenAI API to generate a response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Specify the language model to use
            messages=conversation_history,
        )
        # Extract the AI's reply from the response
        ai_reply = response.choices[0].message.content
        print(f"AI Sales Agent: {ai_reply}")
        
        # Add the AI's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": ai_reply})
        return ai_reply, conversation_history
    except Exception as e:
        # Handle errors gracefully
        print(f"Error: {str(e)}")
