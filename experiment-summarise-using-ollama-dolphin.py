import sys
import os
from summarise_using_ollama_dolphin import summarizeTranscriptFile

if len(sys.argv) == 1:
    #use hardcoded path, because I'm testing
    fileToRead = os.path.join(
        "D:/git/dev/python/podcast-transcriptions/the-eviltester-show/how-to-get-a-job-in-software-testing/how-to-get-a-job-in-software-testing-base.para.txt.md"
    )
else:
    fileToRead = sys.argv[1]

summarizeTranscriptFile(fileToRead)
