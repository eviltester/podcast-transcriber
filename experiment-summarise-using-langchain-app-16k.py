# Test of using langchain with prompt to summarise a text
from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers.utils.logging import set_verbosity_error
import sys
import os

# see also https://github.com/techwithtim/Langchain-Transformers-Python/blob/main/main.py
# https://www.kdnuggets.com/how-to-summarize-texts-bart-model-hugging-face-transformers
# https://www.reddit.com/r/LangChain/comments/1hxeqev/how_to_summarize_large_documents/

set_verbosity_error()

if len(sys.argv) == 1:
    #use hardcoded path, because I'm testing
    fileToRead = os.path.join("D:/git/dev/python/podcast-transcriptions/the-eviltester-show/how-to-get-a-job-in-software-testing/how-to-get-a-job-in-software-testing-base.para.txt.md"
                              )
else:
    fileToRead = sys.argv[1]

if not os.path.isfile(fileToRead):
    print("File does not exist: " + fileToRead)
    exit

print("Getting Ready for summarization")

# Load Hugging Face Summarization Pipeline
summarizer = pipeline("summarization", model="pszemraj/led-large-book-summary", device=0)
#summarizer = pipeline("summarization", model="Falconsai/text_summarization")


# Wrap it inside LangChain
llm = HuggingFacePipeline(pipeline=summarizer)

print("Ready to Summarize")


print("Reading " + fileToRead)
with open(fileToRead,"r") as file:
    filecontents = file.read()


# NOTE led-large-book-summary has token length of about 16k so can handle larger text

print(f"Read File {fileToRead}")

# Create the prompt
template = PromptTemplate.from_template(
    "Summarize the following text:\n\n{text}"
)

summarizer_chain = template | llm

# Execute the summarization chain
summary = summarizer_chain.invoke({"text": filecontents})

# print(filecontents)
# print(filecontents.count(" "))

# summary = summarizer(filecontents, max_length=1000, min_length=100, do_sample=False)

print("\n🔹 **Generated Summary:**")
print(summary)

