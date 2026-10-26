from pypdf import PdfReader

def load_pdf(file_path)->str:
    """Load a PDF file and return its text content."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return ""

def load_text(file_path)->str:
    """Load a text file and return its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading text file: {e}")
        return ""

    
def load_document(file_path:str)->str:
    """Load a document based on its file extension and return its text content."""
    if file_path.endswith('.pdf'):
        return load_pdf(file_path)
    elif file_path.endswith('.txt'):
        return load_text(file_path)
    else:
        print(f"Unsupported file type: {file_path}")
        return ""