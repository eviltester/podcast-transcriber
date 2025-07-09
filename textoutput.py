#
# Text File Output
#

# output a blob of text
def output_raw_text_to_file(fullOutputFilePath, text, outputFileExtension = ".blob.txt"):
    with open(fullOutputFilePath + outputFileExtension, mode="wt", encoding='utf-8') as f:
        f.write(text)
    return fullOutputFilePath + outputFileExtension


# output formatted text with line gaps
def output_formatted_text_with_line_gaps(fullOutputFilePath, segments, outputFileExtension = ".para.md"):
    with open(fullOutputFilePath + outputFileExtension, mode="wt", encoding='utf-8') as f:
        para = ""
        for segment in segments:
            line = segment["text"].strip()
            if(len(line)>0):
                if line[0].isupper():
                    # need a new para
                    if(len(para)>0):
                        # write out old para
                        f.write(para + "\n\n")
                        para = ""
                    # create new para
                    para = para + line
                else:
                    # it is a line to add to old para
                    para = para + " " + line
        if(len(para)>0):
            f.write(para + "\n")
    return fullOutputFilePath + outputFileExtension

# output the exception as the main report
def output_error_as_transcription(fullOutputFilePath, text, outputFileExtension = ".para.md"):
    print("ERROR OUTPUTING TRANSCRIPTION")
    print(fullOutputFilePath)
    print(text)
    with open(fullOutputFilePath + outputFileExtension, mode="wt", encoding='utf-8') as f:
        f.write(text)
    return fullOutputFilePath + outputFileExtension