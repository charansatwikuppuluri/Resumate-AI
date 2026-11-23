import pdfplumber
from docx import Document


def extract_text(file):

    file_name = file.name.lower()

    if file_name.endswith(".pdf"):

        text = ""

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return text

    elif file_name.endswith(".docx"):

        document = Document(file)

        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    else:
        return "Unsupported file format"