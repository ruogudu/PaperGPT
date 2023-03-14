import io

import PyPDF2
import urllib.request


class PDFWrapper:
    """
    Wrapper class for PDF files
    """

    def __init__(self, reader):
        self.pageNum = len(reader.pages)
        self.pages = {i: page.extract_text() for i, page in enumerate(reader.pages)}

    def get_num_pages(self):
        return self.pageNum

    def get_page(self, page_num):
        return self.pages.get(page_num)

    @staticmethod
    def from_url(url):
        with urllib.request.urlopen(url) as f:
            remote_file_bytes = io.BytesIO(f.read())
            reader = PyPDF2.PdfReader(remote_file_bytes)
            return PDFWrapper(reader)

    @staticmethod
    def from_local_file(file_path):
        with open(file_path, "rb") as f:
            local_file_bytes = io.BytesIO(f.read())
            reader = PyPDF2.PdfReader(local_file_bytes)
            return PDFWrapper(reader)
