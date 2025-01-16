import fitz  # PyMuPDF for handling PDFs
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with the API key
client = OpenAI(
    api_key=api_key,
)

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF file.
    """
    try:
        # Open the PDF document using PyMuPDF
        document = fitz.open(pdf_path)
        text = ""

        # Iterate through each page of the document
        for page_num in range(len(document)):
            # Load the page and extract its text
            page = document.load_page(page_num)
            text += page.get_text()

        return text
    except Exception as e:
        # Handle exceptions and return None if an error occurs
        print(f"Error while extracting text from PDF: {str(e)}")
        return None

def summarize_relevant_information(pdf_path):
    """
    Summarize specific parts of the extracted text based on a sales-focused prompt.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Summarized information useful for sales conversations.
    """
    # Extract text from the PDF file
    text = extract_text_from_pdf(pdf_path)

    if text:
        # Define a concise focus prompt for the summarization task
        focus_prompt = "Summarize and extract all relevant parts that could be relevant for a sales conversation."

    # Define the main prompt for OpenAI to summarize the extracted text
    prompt = f"""
    The following text is extracted from a product brochure/manual. Your task is to extract 
    and summarize only the most relevant parts for a sales agent. Include:
    - Key product features
    - Unique selling points
    - Benefits for customers
    - Any standout specifics about the product/service

    Use concise and actionable language that is useful for a sales conversation.

    Text:
    {text}
    """
    try:
        # Use OpenAI API to generate a summarized response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Specify the model to use
            messages=[{"role": "system", "content": focus_prompt}, {"role": "user", "content": prompt}],
            max_tokens=1500,  # Set a token limit for the response
            temperature=0.5,  # Set the response variability
        )
        # Return the summarized content
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Handle exceptions and return None if an error occurs
        print(f"Error while summarizing information: {str(e)}")
        return None
