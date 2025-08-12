from summarization import summarize
from markdownReporter import generateMarkdownSummaryReport

class SummarizeQueueProcessor:

    def __init__(self, summarize_queue, output_path, podcast_list):
        self.summarize_queue = summarize_queue
        self.output_path = output_path
        self.podcastList = podcast_list

    def summarize_all(self):
        # work through the summarization queue
        self.summarize_queue.refresh_cache()

        # summarization works but requires fine tuning
        next_summary = self.summarize_queue.get_next()
        while next_summary is not None:
            # TODO: pass in the basic meta data - podcast title, name, links etc.
            podcast_details = self.find_podcast_in_list(next_summary.podcast_name)


            summarize(next_summary.file)

            generateMarkdownSummaryReport(self.output_path, next_summary.podcast_name, next_summary.episode_title, podcast_details)
            self.summarize_queue.mark_as_done(next_summary)
            self.summarize_queue.save_caches()
            next_summary = self.summarize_queue.get_next()

    def adhoc_summary(self, podcast_name, episode_title):
        return


    def find_podcast_in_list(self, podcast_name):
        if self.podcastList is not None:
            for podcast in self.podcastList:
                if podcast_name == podcast.feedname:
                    return podcast
        return None
