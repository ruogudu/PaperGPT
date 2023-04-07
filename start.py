import os
import urllib
import requests

import questionary
from termcolor import colored

from chatgpt_wrapper import ChatGPTWrapper
from config import local_secret_path
from curated_paper import CuratedPaper
from pdf_wrapper import PDFWrapper


def get_api_key():
    secret_path = os.path.expanduser(local_secret_path)
    temp_api_key = None
    try:
        with open(secret_path, "r") as file:
            data = file.read()
            use_local = questionary.confirm(
                "Found API key from ~/.papergpt/, would you like to use it?"
            ).ask()
            if use_local:
                temp_api_key = data
            else:
                temp_api_key = None
    except FileNotFoundError:
        pass
    if temp_api_key:
        return temp_api_key
    temp_api_key = questionary.text(
        "What is your OpenAI API key? (See https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)"
    ).ask()
    if temp_api_key:
        save = questionary.confirm(
            "Would you like to save the API key to ~/.papergpt/ ?"
        ).ask()
        if save:
            os.makedirs(os.path.dirname(secret_path), exist_ok=True)
            with open(secret_path, "w") as file:
                file.write(temp_api_key)
    return temp_api_key


def get_paper_url():
    while True:
        paper_url = questionary.text(
            "What is the URL of the research paper (PDF)? (Enter 'exit' to exit)"
        ).ask()

        try:
            if paper_url.strip().lower() == "exit":
                exit()
            result = urllib.parse.urlparse(paper_url)
            if all([result.scheme, result.netloc]):
                try:
                    response = requests.head(paper_url)
                    content_type = response.headers["Content-Type"]
                    if content_type == "application/pdf":
                        return paper_url
                    else:
                        print("URL does not point to a PDF file")
                        continue
                except requests.exceptions.RequestException:
                    print("Error: Could not retrieve URL")
                    continue
            else:
                print("URL is not valid")
                continue
        except ValueError:
            print("URL is not valid")
            continue


def load_curated_paper():
    paper_path = questionary.path("What is the path to the cached curated paper?").ask()
    return CuratedPaper.load_from_cache(paper_path)


def save_curated_paper(curated_paper: CuratedPaper):
    paper_path = questionary.path(
        "What is the path to save the cached curated paper?"
    ).ask()
    curated_paper.save_to_local(paper_path)
    print("Saved")


def get_pdf_path():
    while True:
        pdf_path = questionary.path("What is the path to the local PDF file?").ask()
        # Split the file path into root and extension
        root, ext = os.path.splitext(pdf_path)

        # Check if the extension is .pdf
        if ext.lower() != ".pdf":
            print("File path does not end with .pdf")
        else:
            return pdf_path


def conversation(curated_paper: CuratedPaper):
    print("Querying OpenAI...\n")
    print(colored(curated_paper.get_intro(), attrs=["bold"]))
    question = questionary.text(">").ask()
    while True:
        print("Querying OpenAI...\n")
        answer = curated_paper.get_answer_full_process(question)
        print(colored(answer, attrs=["bold"]))
        question = questionary.text(">").ask()


if __name__ == "__main__":
    api_key = get_api_key()
    if api_key is None:
        print("Error getting API key. Exiting...")
        exit(0)
    ChatGPTWrapper.init(api_key)
    load_from_cache = questionary.confirm(
        "Would you like to load curated paper from local cache?"
    ).ask()
    if load_from_cache:
        curated_paper = load_curated_paper()
    else:
        load_local_pdf = questionary.confirm(
            "Would you like to load a local PDF file?"
        ).ask()
        if load_local_pdf:
            pdf_path = get_pdf_path()
            pdf_wrapper = PDFWrapper.from_local_file(pdf_path)
        else:
            url = get_paper_url()
            pdf_wrapper = PDFWrapper.from_url(url)
        print("Curating PaperGPT... This may take several minutes.")
        curated_paper = CuratedPaper(pdf_wrapper)
        save_paper = questionary.confirm(
            "Curation finished. Would you like to save the curated paper to local cache?"
        ).ask()
        if save_paper:
            save_curated_paper(curated_paper)
    conversation(curated_paper)
