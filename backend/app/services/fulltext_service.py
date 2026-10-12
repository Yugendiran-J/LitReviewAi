import os
import requests


def download_pdf(
    pdf_url: str,
    output_path: str
):
    """
    Download a PDF from a direct PDF URL.
    """

    if not pdf_url:
        raise ValueError(
            "PDF URL cannot be empty"
        )

    response = requests.get(
        pdf_url,
        timeout=60
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "content-type",
        ""
    ).lower()

    if (
        "pdf" not in content_type
        and not pdf_url.lower().endswith(".pdf")
    ):
        raise ValueError(
            "The provided URL does not appear to be a PDF."
        )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_path,
        "wb"
    ) as file:

        file.write(response.content)

    return output_path