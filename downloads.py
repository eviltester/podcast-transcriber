import csv
import requests
import os
from urllib.parse import urlparse
from unicodedata import normalize
import re

def filenameify(aString):
    return re.sub('[^A-Za-z0-9_-]',"-", normalize('NFD', aString.lower()).encode('ascii','ignore').decode('utf-8'))

def delete_downloaded_file(downloadUrl, downloadPath):
    # TODO: refactor to remove duplicated path creation code with download_if_not_exists
    parsed_url = urlparse(downloadUrl)
    path = parsed_url.path
    filename = filenameify(os.path.basename(path))
    # todo: could just replace last - with .
    if filename.endswith("-mp3"):
        filename = filename + ".mp3"
    if filename.endswith("-m4a"):
        filename = filename + ".m4a"

    # delete if the filename exists in the download directory
    full_download_path = os.path.join(downloadPath, filename)
    if(os.path.exists(full_download_path)):
        print("Delete File already downloaded to " + downloadPath)
        os.remove(full_download_path)
        return full_download_path

def download_if_not_exists(downloadUrl, downloadPath):

    print("Handling download for " + downloadUrl)
    # from download url get the filename
    parsed_url = urlparse(downloadUrl)
    path = parsed_url.path
    filename = filenameify(os.path.basename(path))
    # todo: could just replace last - with .
    if filename.endswith("-mp3"):
        filename = filename + ".mp3"
    if filename.endswith("-m4a"):
        filename = filename + ".m4a"

    # exit if the filename exists in the download directory
    full_download_path = os.path.join(downloadPath, filename)
    if(os.path.exists(full_download_path)):
       print("File already downloaded to " + downloadPath)
       return full_download_path
    
    print("Downloading " + downloadUrl)
    # download the file to the download direcotory
    # added headers and redirects for buzzsprout downloads
    # http_proxy  = "http://127.0.0.1:8080"
    # https_proxy = "http://127.0.0.1:8080"
    # ftp_proxy   = "http://127.0.0.1:8080"
    #
    # proxies = {
    #     "http"  : http_proxy,
    #     "https" : https_proxy,
    #     "ftp"   : ftp_proxy
    # }
    browserUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    headers = headers={"User-Agent":browserUserAgent}
    audiofile = requests.get(downloadUrl, allow_redirects=True, headers=headers) #,proxies=proxies, verify=False)
    with open(full_download_path, 'wb') as f:
        f.write(audiofile.content)

    print("Downloaded to " + downloadPath)
    return full_download_path

class DownloadFile:
    def __init__(self, podcast_name, episode_title, download_folder, url_to_download):
        self.podcast_name = podcast_name
        self.episode_title = normalize('NFD', episode_title).encode('ascii','ignore').decode('utf-8')
        self.download_folder = download_folder
        self.url = url_to_download

class DownloadQueue:
    def __init__(self, cached_queue_file="", cached_downloaded_queue_file=""):
        self.to_download = []
        self.downloaded = []
        self.cached_queue_file = cached_queue_file
        self.cached_downloaded_queue_file = cached_downloaded_queue_file

        if(cached_queue_file!=""):
            # load the cached queue file
            self.__load_csv_file_as_array_contents(cached_queue_file, self.to_download)
        
        if(cached_downloaded_queue_file!=""):
            # load the cached queue file
            self.__load_csv_file_as_array_contents(cached_downloaded_queue_file, self.downloaded)

    def __load_csv_file_as_array_contents(self, filepath, an_array):
        if(not os.path.exists(filepath)):
            return
        with open(filepath, newline='') as csvfile:
            download_file_list_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in download_file_list_reader:
                an_array.append(DownloadFile(row[0], row[1], row[2], row[3]))

    def __save_array_contents_as_csv_file(self, filepath, an_array):
        with open(filepath, 'w', newline='') as csvfile:
            download_file_list_writer = csv.writer(csvfile, delimiter=',', quotechar='"')
            for item in an_array:
                download_file_list_writer.writerow([item.podcast_name, item.episode_title, item.download_folder, item.url])


    def save_caches(self):
        if(self.cached_queue_file!=""):
            self.__save_array_contents_as_csv_file(self.cached_queue_file, self.to_download)

        if(self.cached_downloaded_queue_file!=""):
            self.__save_array_contents_as_csv_file(self.cached_downloaded_queue_file, self.downloaded)

    def add(self, aDownloadFile: DownloadFile):
        # do not add duplicate urls already in the downloaded queue
        for item in self.downloaded:
            if(item.url == aDownloadFile.url):
                print ("Already downloaded " + item.url)
                return
    
        # do not add duplicate urls already in the download queue
        for item in self.to_download:
            if(item.url == aDownloadFile.url):
                print ("Already in download queue " + item.url)
                return
            
        self.to_download.append(aDownloadFile)

    def get_next(self) -> DownloadFile:
        if len(self.to_download)>0:
            return self.to_download[0]
        else:
            return None
    
    def mark_as_downloaded(self, aDownloadFile: DownloadFile):
        self.to_download.remove(aDownloadFile)
        self.downloaded.append(aDownloadFile)