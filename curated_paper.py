import pickle
import re

from alive_progress import alive_bar
import math

from chatgpt_wrapper import ChatGPTWrapper
from pdf_wrapper import PDFWrapper
from config import VERSION


class CuratedPaper:
    TEMPLATE_SUMMARY = "Please summarize this section of a research paper. Be focused on the information a researcher may find interesting. Include the authors of the paper if you find them. The content you need to summarize is as below. {content}"
    TEMPLATE_INTRO = "Here are the summarizes of each page from a research paper. Please give yourself a proper name given the context of this paper, greet me as this paper, and introduce yourself to me with a summary of the content. Please also provide three questions a researcher may want to ask you like this 'You may want to ask me these questions...<bullet points>'. You don't need to include the original summaries in the response. The summaries are. {all_summaries}"
    TEMPLATE_QUESTION_GET_PAGE = 'Answer the question based on the context below. Keep the answer short and concise. Respond "Unsure about answer" if not sure about the answer. Context: "{all_summaries}" Question: Which page may best answer the question? Please just give me the page number in digits. The question is: {question}'
    TEMPLATE_ANSWER_WITH_PAGE = 'Answer the question as if you are a research paper based on the context below. Keep the answer short and concise. Respond "Unsure about answer" if not sure about the answer. Context: "{content}" Question: {question}'
    TEMPLATE_ANSWER_WITH_SUMMARY = 'Answer the question as if you are a research paper based on the context below. Context: "{all_summaries}" Question: {question}'

    MAX_SUMMARY_TOKEN_COUNT = 4000

    def __init__(self, pdf_wrapper: PDFWrapper):
        self.version = VERSION
        self.pdf_wrapper = pdf_wrapper
        self.page_summary_map = {}
        self.per_page_limit = math.floor(
            self.MAX_SUMMARY_TOKEN_COUNT / pdf_wrapper.get_num_pages()
        )
        self.summary_all = self.curate_summary_all()

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

    def curate_summary_all(self):
        num_pages = self.pdf_wrapper.get_num_pages()
        summaries = []

        with alive_bar(num_pages, length=40, spinner='dots_waves') as bar:
            for p in range(num_pages):
                summary = self.get_summary_for_page(p)
                summary_with_page = f"Page {p}: {summary}"
                summaries.append(summary_with_page)
                bar()

        summary_all = "\n\n".join(summaries)
        return summary_all

    def get_best_page_for_answer(self, question: str):
        prompt = self.TEMPLATE_QUESTION_GET_PAGE.format(
            question=question, all_summaries=self.summary_all
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
            question=question, all_summaries=self.summary_all
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
        prompt = self.TEMPLATE_INTRO.format(all_summaries=self.summary_all)
        answer = ChatGPTWrapper.ask(prompt=prompt)
        return answer

    def save_to_local(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_from_cache(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)
