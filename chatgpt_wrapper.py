import time

import openai

from config import SLEEP_SECONDS_AFTER_CALL


class ChatGPTWrapper:
    """
    Wrapper class for ChatGPT APIs
    """

    @staticmethod
    def init(api_key):
        openai.api_key = api_key

    @staticmethod
    def ask(prompt, role=None, max_tokens=None):
        message = [{"role": "user", "content": prompt}]
        if role:
            message.append(
                {
                    "role": "system",
                    "content": role,
                }
            )
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            max_tokens=max_tokens,
        )

        time.sleep(SLEEP_SECONDS_AFTER_CALL)  # To make OpenAI rate limiter happy

        return completion["choices"][0]["message"]["content"].strip()

    @staticmethod
    def ask_as_researcher(prompt, paper_content, max_tokens=None):
        role_message = (
            "You will answer this question as this research paper itself. "
            + paper_content
        )
        return ChatGPTWrapper.ask(
            prompt=prompt, role=role_message, max_tokens=max_tokens
        )
