import whisper
import os
from textoutput import output_raw_text_to_file, output_formatted_text_with_line_gaps
from srtoutput import output_srt_file

# official whisper output utils
from whisper.utils import get_writer

class Transcriber():

    def __init__(self):
        self.initialized_model_name = ""
        self.initialized_model = None

    def transcribe(self, inputAudioFile, outputFolder, outputFileName, whisper_model="base"):

        # loading the model takes time so only do this once, and only do when transcribing
        if(self.initialized_model_name != whisper_model or self.initialized_model == None):
            # Process the audio file
            print("Loading Whisper Model " + whisper_model)
            self.initialized_model_name = whisper_model
            self.initialized_model = whisper.load_model(whisper_model)

        outputFileFolder = os.path.join(outputFolder, outputFileName)

        # old versions of the app would write directly to the folder
        # fix that here
        looseFiles = [f for f in os.listdir(outputFolder) if os.path.isfile(os.path.join(outputFolder, f))]
        for looseFile in looseFiles:
            print("Migration: moving file to subfolder " + looseFile)
            fullName = os.path.basename(looseFile)
            fileName = os.path.splitext(fullName)
            fileNameNoBase = fileName[0]
            # remove the -base from end
            if(fileNameNoBase.endswith(".blob")):
                fileNameNoBase = fileNameNoBase[:-5]
            if(fileNameNoBase.endswith("-base")):
                fileNameNoBase = fileNameNoBase[:-5]
            # create the folder    
            looseOutputFileFolder = os.path.join(outputFolder, fileNameNoBase)
            if not os.path.exists(looseOutputFileFolder):
                os.makedirs(looseOutputFileFolder)
            # move the file
            os.replace(os.path.join(outputFolder,looseFile), os.path.join(looseOutputFileFolder, fullName))
            

        # output all the files to a folder
        if not os.path.exists(outputFileFolder):
            os.makedirs(outputFileFolder)

        outputFilePath = os.path.join(outputFileFolder, outputFileName)    

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
        result = self.initialized_model.transcribe(inputAudioFile)

        print("Writing transcript " + outputFileName)
        print("To... " + outputFilePath)
        output_raw_text_to_file(outputFilePath + "-" + whisper_model, result["text"])
        output_formatted_text_with_line_gaps(outputFilePath + "-" + whisper_model, result["segments"])
        output_srt_file(outputFilePath + "-" + whisper_model, result["segments"])

        # try the official outputs instead of our hacks
        writer = get_writer("all", str(outputFileFolder))
        writer(result, outputFileName + "out")
        

