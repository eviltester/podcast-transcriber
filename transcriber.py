import whisper
from os.path import join
from textoutput import output_raw_text_to_file, output_formatted_text_with_line_gaps
from srtoutput import output_srt_file

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

        outputFilePath = join(outputFolder, outputFileName)

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
        output_raw_text_to_file(outputFilePath + "-" + whisper_model, result["text"])
        output_formatted_text_with_line_gaps(outputFilePath + "-" + whisper_model, result["segments"])
        output_srt_file(outputFilePath + "-" + whisper_model, result["segments"])
