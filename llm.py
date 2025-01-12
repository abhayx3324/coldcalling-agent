from openai import OpenAI
import pdf_extractor
import json

# Set your OpenAI API key (use a private key)
api_key = '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'

client = OpenAI(
    api_key=api_key,
)

def extract_product_features(product_name, company_name):
    """
    Extract features for the given product name using OpenAI's API.
    """
    prompt = f"""
    You are a marketing assistant. Your job is to extract detailed, marketable features for a product 
    based on its name. The product name is '{product_name}' by '{company_name}'. Generate a list of features that would 
    be appealing to customers and highlight its unique selling points.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Updated to gpt-3.5-turbo
            messages=[{"role": "system", "content": prompt}]
        )
        features = response.choices[0].message.content  # Adjusted response parsing
        return features.strip()
    except Exception as e:
        print(f"Error while extracting features: {str(e)}")
        return "Error extracting product features."
    
def load_product_data():
    file_path="product_data.json"
    try:
        with open(file_path, 'r') as file:
            product_data = json.load(file)
        return product_data
    except Exception as e:
        print(f"Error loading product data: {str(e)}")
        return None

def start_sales_conversation():
    product_data = load_product_data()
    if not product_data:
        return "Error loading product data from the file."

    product_name = product_data.get("productName", "")
    company_name = product_data.get("companyName", "")
    product_description = product_data.get("productDescription", "")
    pdf_description = product_data.get("pdfText", "")
    
    if not pdf_description:
        pdf_description = ""
    product_features = extract_product_features(product_name, company_name)

    # Define the system message with the extracted features
    system_message = f"""
    #Role: (Who they are)

Your are Ravi, an experienced salesperson for'{product_name}' . You are friendly and love to help customers find the right services/products. You will help the customer decide and try making the greatest profit for the business

#Task: (What they do)


You converse with the caller and find out which of our products they are a fit for. Once the customer has decided to buy the product, book them an appointment to buy the product. Persuade the customer to buy the product if they seem disinterested or want to leave the call.
dont use 'how can i assist you' as the user might not know what they want. Instead, ask them if they are interested in the product and talk about the product in 1 short sentence.

#Specifics: (How they do it)

You will introduce yourself and where you work. You will greet the user and try to capture their first and last name. You will then qualify the user about the product. Explain in detail about the product based on what the customer wants. Assist them in into buying the product. Encourage and persuade the customer to consider the product by highlighting its benefits and value, gently reinforcing these points if they seem hesitant or dont want to buy the product. Once this is collected, you ask for their address. You will then capture the date and time they would like an in-person appointment.

#Context

##The Business:
'{product_features}'

##Additional Information:
'{product_description}'
'{pdf_description}'
    """

    conversation_history = [{"role": "system", "content": system_message}]

    # Start the sales conversation
    conversation_history.append({"role": "assistant", "content": f"Hello! My name is Ravi from {company_name}. May I have your first and last name, please?"})
    # Incorporate the user's name into the conversation
    # print(f"AI Sales Agent: Nice to meet you, {user_name}. How can I assist you today?")

    return conversation_history




def get_ai_response(user_input, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Updated to gpt-3.5-turbo
            messages=conversation_history,
        )
        ai_reply = response.choices[0].message.content  # Adjusted response parsing
        print(f"AI Sales Agent: {ai_reply}")
        conversation_history.append({"role": "assistant", "content": ai_reply})
        return ai_reply, conversation_history
    except Exception as e:
        print(f"Error: {str(e)}")
