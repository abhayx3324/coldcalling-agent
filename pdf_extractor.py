import fitz  # PyMuPDF
from openai import OpenAI

# Set your OpenAI API key
api_key = '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'

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
)

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    """
    try:
        document = fitz.open(pdf_path)
        text = ""

        # Iterate through each page
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()

        return text
    except Exception as e:
        print(f"Error while extracting text from PDF: {str(e)}")
        return None

def summarize_relevant_information(pdf_path):
    """
    Summarize specific parts of the text based on a provided focus prompt.
    """
    text = extract_text_from_pdf(pdf_path)

    if text:
        focus_prompt = "Summarize and extract all relevant parts that could be relevant for a sales conversations."

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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": focus_prompt}, {"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error while summarizing information: {str(e)}")
        return None