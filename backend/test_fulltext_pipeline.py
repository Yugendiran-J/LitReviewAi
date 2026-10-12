import os

from app.services.pdf_service import (
    extract_text_from_pdf,
    extract_pages_from_pdf
)


PDF_PATH = "documents/test.pdf"


if not os.path.exists(PDF_PATH):

    raise FileNotFoundError(
        f"Test PDF not found: {PDF_PATH}"
    )


print("\nFULL-TEXT PIPELINE TEST")
print("=======================")


# ----------------------------------------------------------
# 1. Extract complete text
# ----------------------------------------------------------

full_text = extract_text_from_pdf(
    PDF_PATH
)

print("\nFULL TEXT")
print("=========")

print(
    "Characters extracted:",
    len(full_text)
)


# ----------------------------------------------------------
# 2. Extract page-wise text
# ----------------------------------------------------------

pages = extract_pages_from_pdf(
    PDF_PATH
)

print("\nPAGES")
print("=====")

print(
    "Total pages:",
    len(pages)
)


# ----------------------------------------------------------
# 3. Show first page
# ----------------------------------------------------------

if pages:

    print("\nFIRST PAGE PREVIEW")
    print("==================")

    print(
        pages[0]["text"][:1000]
    )