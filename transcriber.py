import whisper
import os
from textoutput import output_raw_text_to_file, output_formatted_text_with_line_gaps
from srtoutput import output_srt_file
from downloads import download_if_not_exists

#
# Main App code
#


'''
Todo List
TODO: Given an list of RSS feeds parse and process
TODO: Given an RSS feed parse and find new episodes, to add to download queue
TODO: Given a list of urls in a download queue, download and parse the files
- Given a url, download the mp3 and transcribe
'''


# Data and Configuration
downloadUrl="https://downloads.pod.co/558da60d-be59-43be-afee-67c93f05c5e0/4c20f2bf-814a-47d3-90ca-42ede6325c2e.mp3"
downloadPath = "/Users/alanrichardson/Downloads"
outputPath = "/Users/alanrichardson/Documents/docs-git/dev/python/podcast-transcriptions"
outputFileName = "testpodcast-transcription"
whisperModel = "base"
outputFilePath = os.path.join(outputPath, outputFileName)


# download the next podcast
inputAudioFile = download_if_not_exists(downloadUrl, downloadPath)

# Process the audio file
print("Loading Whisper Model " + whisperModel)
model = whisper.load_model(whisperModel)

'''
 options to the transcribe are visible in the code
 https://github.com/openai/whisper/blob/f572f2161ba831bae131364c3bffdead7af6d210/whisper/transcribe.py#L38

 Returns
    -------
    A dictionary containing the resulting text ("text") and segment-level details ("segments"), and
    the spoken language ("language"), which is detected when `decode_options["language"]` is None

segments returns the main parsed entries

segment {'id': 672, 'seek': 171276, 'start': 1718.76, 'end': 1720.08, 'text': ' Thanks very much. Bye.', 'tokens': [50664, 2561, 588, 709, 13, 4621, 13, 50730], 'temperature': 0.0, 'avg_logprob': -0.23039730389912924, 'compression_ratio': 1.2966101694915255, 'no_speech_prob': 0.0013797399587929249}]

Speaker identification?
- https://lablab.ai/t/whisper-transcription-and-speaker-identification
- https://colab.research.google.com/drive/1V-Bt5Hm2kjaDb4P1RyMSswsDKyrzc2-3?usp=sharing#scrollTo=O0_tup8RAyBy
- https://ramsrigoutham.medium.com/openais-whisper-7-must-know-libraries-and-add-ons-built-on-top-of-it-10825bd08f76
'''
print("Transcribing File " + inputAudioFile)
result = model.transcribe(inputAudioFile)

print("Writing transcript " + outputFileName)
output_raw_text_to_file(outputFilePath, result["text"])
output_formatted_text_with_line_gaps(outputFilePath, result["segments"])
output_srt_file(outputFilePath, result["segments"])

print("All Done")