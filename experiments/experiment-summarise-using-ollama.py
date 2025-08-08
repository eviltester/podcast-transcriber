# Test of using langchain with prompt to summarise a text
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import sys
import os

# see also https://github.com/techwithtim/Langchain-Transformers-Python/blob/main/main.py
# https://www.kdnuggets.com/how-to-summarize-texts-bart-model-hugging-face-transformers
# https://www.reddit.com/r/LangChain/comments/1hxeqev/how_to_summarize_large_documents/


if len(sys.argv) == 1:
    #use hardcoded path, because I'm testing
    fileToRead = os.path.join(
        "D:/git/dev/python/podcast-transcriptions/the-eviltester-show/how-to-get-a-job-in-software-testing/how-to-get-a-job-in-software-testing-base.para.txt.md"
    )
else:
    fileToRead = sys.argv[1]

if not os.path.isfile(fileToRead):
    print("File does not exist: " + fileToRead)
    exit

print("Reading File:" + fileToRead)
with open(fileToRead,"r") as file:
    filecontents = file.read()


print(f"Read File {fileToRead}")

print("Getting Ready for summarization")

# https://python.langchain.com/api_reference/ollama/chat_models/langchain_ollama.chat_models.ChatOllama.html
# any models used should first have been pulled into ollama - `ollama pull llama3.1`
llama31 = ChatOllama(
    model="llama3.1",
    temperature=0,
    # other params...
)

print("Starting to Summarize")

#controlText = "When answering You SHOULD NOT include any other text in the response. You should only answer the prompt. Do not include any follow on questions or prompt the user for follow on action. "
gemmaControlText = "\n\n Add '&&&&&' before your response content. Add 'XXXXX' after your response."
# Create the prompt
summarytemplate = PromptTemplate.from_template(
    gemmaControlText + "Summarize the following text:\n\n{text}" + "\n\n" + gemmaControlText
)

llamasummarizer_chain = summarytemplate | llama31

# Execute the summarization chain
llamaShortSummary = llamasummarizer_chain.invoke({"text": filecontents})

print("Starting to Summarize with Gemma")

gemma3 = ChatOllama(
    model="gemma3",
    temperature=0,
    # other params...
)

gemma3summarizer_chain = summarytemplate | gemma3

# gemma provides a longer summary
#gemma3Summary = gemma3summarizer_chain.invoke({"text": filecontents})

gemma3 = ChatOllama(
    model="gemma3",
    temperature=0,
    # other params...
)

actionItemsTemplate = PromptTemplate.from_template(
    gemmaControlText + "Create a checklist of actions the reader can take to implement the information in this text: \n\n {text} \n\n{gemmaControlText}"
)

gemma3Actions_chain = actionItemsTemplate | gemma3

gemma3ActionsSummary = gemma3Actions_chain.invoke({"text": filecontents, "gemmaControlText": gemmaControlText})

print("\n🔹 **Generated Summary:**")
#print(llamaShortSummary.content)
#print(gemma3Summary.content)
print(gemma3ActionsSummary.content)

