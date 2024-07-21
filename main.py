import asyncio
import inspect
import json
import os
import sys
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    Destination,
    Fit,
    IndirectObject,
    NameObject,
    NumberObject,
    PdfObject,
    TextStringObject,
)
from pyppeteer import launch


def download_pages(links, postprocessing=[], html_dir="html/"):
    os.makedirs(html_dir, exist_ok=True)
    meta = []

    for i, url in enumerate(links):
        response = requests.get(url)

        print(f"Downloading HTML: {i}/{len(links)-1}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            for func in postprocessing:
                func(i, response, soup)

            title = (
                soup.select_one("title").get_text()
                if soup.select_one("title")
                else os.path.basename(url)
            )

            path = os.path.join(html_dir, f"{i}.html")
            with open(path, "w") as file:
                file.write(soup.prettify())

            meta.append({"id": i, "title": title, "url": url})

        else:
            print(f"Error downloading HTML page (code: {response.status_code} ): {url}")
            exit(1)

    with open(os.path.join(html_dir, "metadata.json"), "w") as f:
        f.write(json.dumps(meta))


async def html_to_pdf(
    html_dir="html/", pdf_dir="pdf/", browser_opts={"headless": True}
):
    os.makedirs(pdf_dir, exist_ok=True)

    with open(os.path.join(html_dir, "metadata.json")) as f:
        html_metadata = json.load(f)

    print("Starting browser...")
    browser = await launch(**browser_opts)

    for i, html_m in enumerate(html_metadata):
        print(f"Converting HTML to PDF: {i}/{len(html_metadata)-1}")

        id = html_m["id"]

        html_path = os.path.join(html_dir, f"{id}.html")
        pdf_path = os.path.join(pdf_dir, f"{id}.pdf")

        page = await browser.newPage()

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        await page.goto("about:blank")
        await page.setContent(content)
        await page.waitFor(5000)  # wait 5 secs for page to load
        await page.pdf(
            {
                "path": pdf_path,
                "format": "A4",
                "margin": {
                    "top": "0.4 in",
                    "bottom": "0.4 in",
                    "right": "0.4 in",
                    "left": "0.4 in",
                },
            }
        )
        await page.close()

    with open(os.path.join(pdf_dir, "metadata.json"), "w") as f:
        f.write(json.dumps(html_metadata))

    await browser.close()


def merge_pdf(pdf_dir="pdf/", output_path="output.pdf"):

    print("Merging PDFs...")

    with open(os.path.join(pdf_dir, "metadata.json")) as f:
        pdf_metadata = json.load(f)

    writer = PdfWriter()
    b = 0

    bookmarks = {}
    for pdf_m in pdf_metadata:
        pdf_path = os.path.join(pdf_dir, f"{pdf_m['id']}.pdf")
        reader = PdfReader(pdf_path)

        writer.add_outline_item(pdf_m["title"], b)

        bookmarks.update(
            {
                pdf_m["url"]: {
                    "title": pdf_m["title"],
                    "page": b,
                }
            }
        )

        for page in reader.pages:
            writer.add_page(page)
            b += 1

    # replace url to internal links
    for page in writer.pages:

        annot: IndirectObject
        for annot in page.get("/Annots", []):
            annot_obj: PdfObject = annot.get_object()

            if "/A" not in annot_obj:
                continue

            link_obj = annot_obj["/A"]

            # Cleanup uri
            uri = link_obj.get("/URI", "")
            parsed_uri = urlparse(uri)
            uri = urlunparse(
                (parsed_uri.scheme, parsed_uri.netloc, parsed_uri.path, "", "", "")
            )

            if uri in bookmarks:
                link_obj.pop("/URI")
                link_obj[TextStringObject("/S")] = NameObject("/GoTo")
                link_obj[TextStringObject("/D")] = Destination(
                    bookmarks[uri]["title"],
                    NumberObject(bookmarks[uri]["page"]),
                    Fit(
                        "/XYZ",
                        (None, None, 0),
                    ),
                )

    writer.write(output_path)
    writer.close()


from html_processing import *
from urls import LINKS

if __name__ == "__main__":

    html_files = download_pages(
        LINKS,
        [
            obj
            for name, obj in inspect.getmembers(sys.modules[__name__])
            if (inspect.isfunction(obj) and name.startswith("html_process_"))
        ],
    )

    event = asyncio.get_event_loop()

    pdf_files = event.run_until_complete(html_to_pdf())

    merge_pdf(output_path="composing_programs.pdf")
