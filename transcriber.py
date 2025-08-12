import whisper
import os
import time
from textoutput import output_raw_text_to_file, output_formatted_text_with_line_gaps, output_error_as_transcription
from srtoutput import output_srt_file
#import whisperx

# official whisper output utils
from whisper.utils import get_writer

# diarization notes for future speaker identification:
# https://github.com/openai/whisper/discussions/264
# https://community.openai.com/t/best-solution-for-whisper-diarization-speaker-labeling/505922/21
# https://github.com/MahmoudAshraf97/whisper-diarization

class Transcriber():

    def __init__(self):
        self.initialized_model_name = ""
        self.initialized_model = None

    # TODO: if there is an error then the job should go in an error queue to allow recovery or retry
    def transcribe(self, inputAudioFile, outputFolder, outputFileName, whisper_model="base"):

        # whisperx - https://github.com/m-bain/whisperX?tab=readme-ov-file
        device = "cuda"
        batch_size = 16 # reduce if low on GPU mem
        compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)

        # loading the model takes time so only do this once, and only do when transcribing
        if(self.initialized_model_name != whisper_model or self.initialized_model == None):
            # Process the audio file
            modelLoadingStartTime = time.time()
            print("Loading Whisper Model " + whisper_model)
            self.initialized_model_name = whisper_model
            # whisper
            self.initialized_model = whisper.load_model(whisper_model)
            # whisper x
            # self.initialized_model =whisperx.load_model("large-v2", device, compute_type=compute_type)
            modelLoadingEndTime = time.time()
            print('TIME: to load model - ', modelLoadingEndTime - modelLoadingStartTime, 'seconds')

        outputFileFolder = os.path.join(outputFolder, outputFileName)


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
        
        see also https://github.com/SYSTRAN/faster-whisper
        
        https://www.reddit.com/r/LocalLLaMA/comments/1brqwun/i_compared_the_different_open_source_whisper/
        
        '''
        print("Transcribing File " + inputAudioFile)
        transcribeStartTime  = time.time()

        try:
            # whisper x
            # audio = whisperx.load_audio(inputAudioFile)
            # result = self.initialized_model.transcribe(audio, batch_size=batch_size)
            #model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
            #result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

            # whisper
            result = self.initialized_model.transcribe(inputAudioFile)


            transcribeEndTime  = time.time()
            print('TIME: to transcribe - ', transcribeEndTime - transcribeStartTime, 'seconds')


            print("Writing transcript " + outputFileName)
            print("To... " + outputFilePath)
            outputStartTime  = time.time()
            output_raw_text_to_file(outputFilePath + "-" + whisper_model, result["text"])
            fileToSummarize = output_formatted_text_with_line_gaps(outputFilePath + "-" + whisper_model, result["segments"])
            output_srt_file(outputFilePath + "-" + whisper_model, result["segments"])

            # try the official outputs instead of our hacks
            writer = get_writer("all", str(outputFileFolder))
            writer(result, outputFileName + "out")
            outputEndTime  = time.time()
            print('TIME: to output - ', outputEndTime - outputStartTime, 'seconds')
            return fileToSummarize
        except Exception as e:
            output_error_as_transcription(outputFilePath + "-" + whisper_model + "-ERROR", "ERROR TRANSCRIBING " + repr(e))
            outputEndTime  = time.time()
            print('TIME: to fail - ', outputEndTime - transcribeStartTime, 'seconds')
            return "ERROR"


        

