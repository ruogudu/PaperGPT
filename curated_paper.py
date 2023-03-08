import pickle
import re

import math

from chatgpt_wrapper import ChatGPTWrapper
from pdf_wrapper import PDFWrapper
from config import VERSION


class CuratedPaper:
    TEMPLATE_SUMMARY = "Please summarize this section of a research paper. Be focused on the information a researcher may find interesting. Include the authors of the paper if you find them. The content you need to summarize is as below. {content}"
    TEMPLATE_INTRO = "Here are the summarizes of each page from a research paper. Please give yourself a proper name given the context of this paper, greet me as this paper, and introduce yourself to me. After the summary, please also provide three questions a researcher may want to ask you like this 'You may want to ask me these questions...'. You don't need to include the original summaries in the response. The summaries are. {all_summaries}"
    TEMPLATE_QUESTION_GET_PAGE = 'You are a research paper. Here is a message to you and the summarizes of each page from the research paper. Please tell me which page may best respond to the message. Please only respond the page number in digits without further explanation. If you are not sure, respond "None". The message is. "{question}" The summaries of each page are. {all_summaries}'
    TEMPLATE_ANSWER_WITH_PAGE = 'You are a research paper. Please succinctly respond to this message with this section of the research paper. The message is. "{question}" The section of the research paper is. {content}'
    TEMPLATE_ANSWER_WITH_SUMMARY = 'You are a research paper. Please succinctly respond to this message to you. The message is. "{question}" The research paper is. {all_summaries}'

    MAX_SUMMARY_TOKEN_COUNT = 4000

    def __init__(self, pdf_wrapper: PDFWrapper):
        self.version = VERSION
        self.pdf_wrapper = pdf_wrapper
        self.page_summary_map = {}
        self.per_page_limit = math.floor(
            self.MAX_SUMMARY_TOKEN_COUNT / pdf_wrapper.get_num_pages()
        )
        self.summary_all = None
        self.get_summary_all()

    def get_summary_for_page(self, page_num: int):
        if page_num in self.page_summary_map:
            return self.page_summary_map[page_num]
        page_text = self.pdf_wrapper.get_page(page_num)
        prompt = self.TEMPLATE_SUMMARY.format(content=page_text)
        answer = ChatGPTWrapper.ask(
            prompt=prompt,
            max_tokens=self.per_page_limit,
        )
        return answer

    def get_summary_all(self):
        if self.summary_all is not None:
            return self.summary_all
        num_pages = self.pdf_wrapper.get_num_pages()
        summaries = []
        for p in range(num_pages):
            summary = self.get_summary_for_page(p)
            summary_with_page = f"Page {p}: {summary}"
            summaries.append(summary_with_page)
            print(f"Page {p+1} curated.")
        self.summary_all = "\n\n".join(summaries)
        return self.summary_all

    def get_best_page_for_answer(self, question: str):
        prompt = self.TEMPLATE_QUESTION_GET_PAGE.format(
            question=question, all_summaries=self.get_summary_all()
        )
        answer = ChatGPTWrapper.ask(prompt=prompt, max_tokens=10)
        page_num = re.search(r"\d+", answer)
        if page_num is None:
            return None
        return int(page_num.group())

    def get_answer_from_page(self, question: str, page_num: int):
        page_text = self.pdf_wrapper.get_page(page_num)
        prompt = self.TEMPLATE_ANSWER_WITH_PAGE.format(
            question=question,
            content=page_text,
        )
        answer = ChatGPTWrapper.ask(prompt=prompt)
        answer += f" (Page {page_num+1})"
        return answer

    def get_answer_from_summary(self, question: str):
        prompt = self.TEMPLATE_ANSWER_WITH_SUMMARY.format(
            question=question, all_summaries=self.get_summary_all()
        )
        answer = ChatGPTWrapper.ask(prompt=prompt)
        return answer

    def get_answer_full_process(self, question: str):
        best_page = self.get_best_page_for_answer(question)
        if best_page is None:
            answer = self.get_answer_from_summary(question)
        else:
            answer = self.get_answer_from_page(question, best_page)
        return answer

    def get_intro(self):
        prompt = self.TEMPLATE_INTRO.format(all_summaries=self.get_summary_all())
        answer = ChatGPTWrapper.ask(prompt=prompt)
        return answer

    def save_to_local(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_from_cache(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)