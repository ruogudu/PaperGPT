import io

import PyPDF2
import urllib.request


class PDFWrapper:
    """
    Wrapper class for PDF files
    """

    def __init__(self, url):
        self.url = url
        self.pages = {}
        with urllib.request.urlopen(url) as f:
            remote_file_bytes = io.BytesIO(f.read())
            reader = PyPDF2.PdfReader(remote_file_bytes)
            self.pageNum = len(reader.pages)

            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                self.pages[i] = text

    def get_num_pages(self):
        return self.pageNum

    def get_page(self, page_num):
        return self.pages[page_num]
