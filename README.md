# PaperGPT
PaperGPT is a tool that uses OpenAI's GPT-3.5-Turbo language model (same that powers ChatGPT) to answer questions about research papers. With PaperGPT, you can ask questions about a research paper and get relevant answers in natural language.

# Installation
To install PaperGPT, first clone the repository:
```
git clone git@github.com:ruogudu/PaperGPT.git
```

Then, navigate to the papergpt directory and run:
```
pip3 install -r requirements.txt
```

# Usage

To use PaperGPT, navigate to the PaperGPT directory and run:
```
python3 start.py
```

This will prompt you to enter your OpenAI API key. If you don't have an API key, you can sign up for one on the [OpenAI website](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key).

Next, you will be prompted to enter the URL of the research paper you want to query. PaperGPT only works with PDFs, so make sure the URL points to a PDF file.

If this is your first time using PaperGPT with this research paper, it will take several minutes to "curate" the paper. This process involves extracting key information from the paper and preparing it for input to the language model. Once the curation process is complete, you can begin asking questions about the paper.

To ask a question, simply type it in at the > prompt and press Enter. PaperGPT will query the language model and return the most relevant answer.

# Demo
Here's an example of how to use PaperGPT:

![image](https://user-images.githubusercontent.com/10095870/223643424-bcaeff26-e7b4-4cef-b9e0-fccebb30861c.png)

In this example, we first enter our OpenAI API key and specify that we want to curate a new research paper. We then enter the URL of the research paper and specify that we want to save the curated paper to a local file. After the curation process is complete, we will see greetings from the papaer. Then we can ask a question and get a relevant answer in natural language.
