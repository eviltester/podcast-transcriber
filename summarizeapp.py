# quick test to see if we can summarize a transcript

import torch
import os
from transformers import pipeline
from langchain.text_splitter import TokenTextSplitter

model_creator = "facebook"
model_name = "bart-large-cnn"

fileToRead = os.path.join("/Users/alanrichardson/Documents/docs-git/dev/python/podcast-transcriptions",
                  "test-entities-cases-transcript.txt"
                  )

print("Getting Ready for summarization")

if torch.cuda.is_available():
    print("Using CPU for summarization")
    summarizer = pipeline("summarization", model=f"{model_creator}/{model_name}", device=0)
else:
    print("Using GPU for summarization")
    summarizer = pipeline("summarization", model=f"{model_creator}/{model_name}")

print("Ready to Summarize")


print("Reading " + fileToRead)
file=open(fileToRead,"r")
filecontents = file.read()
file.close()

print(f"Read File {fileToRead}")

# split large content into smaller chunks
# splitting text information
#  https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/split_by_token

chunk_size = 250
max_summary_size = chunk_size/2

text_splitter = TokenTextSplitter(
    chunk_size=chunk_size, chunk_overlap=0
)

texts = text_splitter.split_text(filecontents)

# Summarize the chunks

print("Summarizing..." + str(len(texts)) + " sections")

summaryLines = []

for text in texts:
    print("Segment:\n\n" + text.replace("\r\n", " ").replace("\n", " ")  + "\n\n")
    summary = summarizer(text, max_length=int(max_summary_size), min_length=30, do_sample=False)
    summaryLine = summary.pop()['summary_text']
    print(f"Summary:\n\n\n{summaryLine}\n\n")
    summaryLines.append(summaryLine)


# Output the summary

print("\n\n---\n\n")

outputSummary = ""

for summaryLine in summaryLines:
    outputSummary = outputSummary + "\n\n" + summaryLine

print(outputSummary)

with open(fileToRead + ".summary.txt", 'w') as f:
    f.write(outputSummary)