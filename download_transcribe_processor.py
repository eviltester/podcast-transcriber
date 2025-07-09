from transcriber import Transcriber
from downloads import download_if_not_exists, filenameify
import os
from summarization import SummarizeFile

class DownloadAndTranscribeProcessor:

    def __init__(self, download_queue, summarize_queue, download_path, output_path):
        self.download_queue = download_queue
        self.summarize_queue = summarize_queue
        self.transcriber = Transcriber()
        self.download_path = download_path
        self.output_path = output_path

    def download_transcribe_and_queue_for_summarization(self):

        next_download = self.download_queue.get_next()
        # download and transcribe the next podcast
        while next_download != None:
            #print(yaml.dump(download_queue, indent=2))

            # TODO: if there is an error downloading then add to an error queue
            print("Processing: ", next_download.podcast_name, " - ", next_download.episode_title)

            inputAudioFile = download_if_not_exists(next_download.url, self.download_path)

            transcriptionFileName = filenameify(next_download.episode_title)
            transcriptionOutputFolderName = filenameify(next_download.podcast_name)
            transcriptionOutputFolder = os.path.join(self.output_path, transcriptionOutputFolderName)
            if not os.path.exists(transcriptionOutputFolder):
                os.makedirs(transcriptionOutputFolder)

            # TODO: if there is an error here add it to an error queue
            fileToSummarize = self.transcriber.transcribe(inputAudioFile, transcriptionOutputFolder, transcriptionFileName)

            if fileToSummarize == "ERROR":
                # add to error queue
                print("ERROR")

            # now that it is transcribed, add it to the summary queue
            if fileToSummarize != "ERROR":
                self.summarize_queue.add(SummarizeFile(next_download.podcast_name, next_download.episode_title, fileToSummarize))
                self.summarize_queue.save_caches()

            self.download_queue.mark_as_downloaded(next_download)
            self.download_queue.save_caches()
            next_download = self.download_queue.get_next()