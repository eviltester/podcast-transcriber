import csv
import os
from unicodedata import normalize
from summarise_using_ollama import summarizeTranscriptFile

def summarize(aFilePath):
    print("Handling summary for " + aFilePath)
    summarizeTranscriptFile(aFilePath)

class SummarizeFile:
    def __init__(self, podcast_name, episode_title, transcriptFile):
        self.podcast_name = podcast_name
        self.episode_title = normalize('NFD', episode_title).encode('ascii','ignore').decode('utf-8')
        self.file = transcriptFile

class SummarizeQueue:
    def __init__(self, cached_queue_file="", cached_done_queue_file=""):
        self.todo = []
        self.done = []
        self.cached_queue_file = cached_queue_file
        self.cached_done_queue_file = cached_done_queue_file

        if(cached_queue_file!=""):
            # load the cached queue file
            self.__load_csv_file_as_array_contents(cached_queue_file, self.todo)
        
        if(cached_done_queue_file!=""):
            # load the cached queue file
            self.__load_csv_file_as_array_contents(cached_done_queue_file, self.done)

    def __load_csv_file_as_array_contents(self, filepath, an_array):
        if(not os.path.exists(filepath)):
            return
        with open(filepath, newline='') as csvfile:
            download_file_list_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in download_file_list_reader:
                an_array.append(SummarizeFile(row[0], row[1], row[2]))

    def __save_array_contents_as_csv_file(self, filepath, an_array):
        with open(filepath, 'w', newline='') as csvfile:
            download_file_list_writer = csv.writer(csvfile, delimiter=',', quotechar='"')
            for item in an_array:
                download_file_list_writer.writerow([item.podcast_name, item.episode_title, item.file])


    def save_caches(self):
        if(self.cached_queue_file!=""):
            self.__save_array_contents_as_csv_file(self.cached_queue_file, self.todo)

        if(self.cached_done_queue_file!=""):
            self.__save_array_contents_as_csv_file(self.cached_done_queue_file, self.done)

    def add(self, anItem: SummarizeFile):
        # do not add duplicate files already in the done queue
        for item in self.done:
            if(item.file == anItem.file):
                print ("Already summarized " + item.file)
                return
    
        # do not add duplicate files already in the todo queue
        for item in self.todo:
            if(item.file == anItem.file):
                print ("Already in to summarize queue " + item.file)
                return
            
        self.todo.append(anItem)

    def get_next(self) -> SummarizeFile:
        if len(self.todo)>0:
            return self.todo[0]
        else:
            return None
    
    def mark_as_done(self, anItem: SummarizeFile):
        self.todo.remove(anItem)
        self.done.append(anItem)