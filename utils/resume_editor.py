
from io import BytesIO

import pdfplumber
from docx import Document


# =====================================================
# TEXT REPLACEMENT
# =====================================================

def replace_text_in_paragraph(paragraph, old_text, new_text):
    """Replace text while retaining the first affected run's formatting."""

    full_text = paragraph.text

    if old_text not in full_text:
        return False

    start = full_text.find(old_text)
    end = start + len(old_text)

    positions = []
    current_position = 0

    for run in paragraph.runs:
        run_start = current_position
        run_end = current_position + len(run.text)

        positions.append((run, run_start, run_end))
        current_position = run_end

    affected = [
        item for item in positions
        if item[1] < end and item[2] > start
    ]

    if not affected:
        return False

    first_run = affected[0][0]

    first_start = start - affected[0][1]
    first_end = min(end, affected[0][2]) - affected[0][1]

    prefix = first_run.text[:first_start]

    suffix = affected[-1][0].text[
        max(0, end - affected[-1][1]):
    ]

    first_run.text = prefix + new_text + suffix

    for run, run_start, run_end in affected[1:]:
        run.text = ""

    return True


def replace_in_paragraphs(paragraphs, old_text, new_text):
    """Search paragraphs and replace the first matching occurrence."""

    for paragraph in paragraphs:

        if replace_text_in_paragraph(
            paragraph, old_text, new_text
        ):
            return True

    return False


def replace_in_tables(tables, old_text, new_text):
    """Search text inside tables."""

    for table in tables:

        for row in table.rows:

            for cell in row.cells:

                if replace_in_paragraphs(
                    cell.paragraphs, old_text, new_text
                ):
                    return True

                if replace_in_tables(
                    cell.tables, old_text, new_text
                ):
                    return True

    return False


def apply_correction(document, old_text, new_text):
    """Apply one correction to a Word document."""

    if not old_text or not new_text:
        return False

    if replace_in_paragraphs(
        document.paragraphs, old_text, new_text
    ):
        return True

    if replace_in_tables(
        document.tables, old_text, new_text
    ):
        return True

    for section in document.sections:

        if replace_in_paragraphs(
            section.header.paragraphs, old_text, new_text
        ):
            return True

        if replace_in_paragraphs(
            section.footer.paragraphs, old_text, new_text
        ):
            return True

    return False


# =====================================================
# PDF TO WORD CONVERSION
# =====================================================

def convert_pdf_to_docx(pdf_file):
    """
    Extract text from a PDF and reconstruct it as a DOCX.

    This preserves readable text and basic paragraph structure,
    but does not reproduce the exact PDF layout.
    """

    document = Document()

    document.add_heading("Corrected Resume", level=0)

    with pdfplumber.open(pdf_file) as pdf:

        for page_number, page in enumerate(pdf.pages):

            page_text = page.extract_text()

            if not page_text:
                continue

            lines = page_text.splitlines()

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                # Basic heading detection
                if (
                    len(line) < 65
                    and line.isupper()
                    and any(char.isalpha() for char in line)
                ):
                    document.add_heading(line, level=1)

                else:
                    document.add_paragraph(line)

            # Keep page breaks where possible
            if page_number < len(pdf.pages) - 1:
                document.add_page_break()

    return document


# =====================================================
# CREATE CORRECTED DOCX
# =====================================================

def create_corrected_docx(
    original_file,
    corrections,
    file_type="docx"
):
    """
    Create a corrected DOCX from either a DOCX or PDF.

    corrections format:
    [
        {
            "exact_text": "Original sentence",
            "suggestion": "Corrected sentence"
        }
    ]

    Returns:
        output_file, applied, not_found
    """

    if file_type.lower() == "pdf":

        document = convert_pdf_to_docx(original_file)

    elif file_type.lower() == "docx":

        document = Document(original_file)

    else:

        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

    applied = []
    not_found = []

    for correction in corrections:

        old_text = correction.get("exact_text", "")
        new_text = correction.get("suggestion", "")

        success = apply_correction(
            document,
            old_text,
            new_text
        )

        if success:
            applied.append(correction)

        else:
            not_found.append(correction)

    output = BytesIO()

    document.save(output)

    output.seek(0)

    return output, applied, not_found
