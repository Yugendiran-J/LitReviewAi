import fitz


def extract_text_from_pdf(pdf_path: str) -> str:
    document = fitz.open(pdf_path)

    full_text = []

    for page in document:
        text = page.get_text()

        if text.strip():
            full_text.append(text)

    document.close()

    return "\n".join(full_text)


def extract_pages_from_pdf(pdf_path: str):
    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text()

        if text.strip():
            pages.append({
                "page_number": page_number,
                "text": text
            })

    document.close()

    return pages