import fitz,os



def process_text(file_path):
    
    doc = fitz.open(file_path)

    # text_by_page = []
    text = ""

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        # text_by_page.append(page.get_text())
        text += page.get_text()

    # print(text_by_page[0])

    # print(text)

    return text

def get_pdf_metadata(file_path):
    """Extract the title of a book from its PDF metadata."""
    doc = fitz.open(file_path)
    metadata = doc.metadata
    return metadata

def get_file_name (file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0] 
    return file_name

def get_file_extension(file_path):  
    file_extension = os.path.splitext(file_path)[1] 
    return file_extension