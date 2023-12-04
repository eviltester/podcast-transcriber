#
# Text File Output
#

# output a blob of text
def output_raw_text_to_file(fullOutputFilePath, text, outputFileExtension = ".blob.txt"):
    with open(fullOutputFilePath + outputFileExtension, mode="wt", encoding='utf-8') as f:
        f.write(text)


# output formatted text with line gaps
def output_formatted_text_with_line_gaps(fullOutputFilePath, segments, outputFileExtension = ".para.txt"):
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
