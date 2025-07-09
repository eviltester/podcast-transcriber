from summarization import summarize
from markdownReporter import generateMarkdownSummaryReport

class SummarizeQueueProcessor:

    def __init__(self, summarize_queue, output_path):
        self.summarize_queue = summarize_queue
        self.output_path = output_path

    def summarize_all(self):
        # work through the summarization queue
        self.summarize_queue.refresh_cache()

        # summarization works but requires fine tuning
        next_summary = self.summarize_queue.get_next()
        while next_summary != None:
            # TODO: pass in the basic meta data - podcast title, name, links etc.
            summarize(next_summary.file)

            generateMarkdownSummaryReport(self.output_path, next_summary.podcast_name, next_summary.episode_title)
            self.summarize_queue.mark_as_done(next_summary)
            self.summarize_queue.save_caches()
            next_summary = self.summarize_queue.get_next()