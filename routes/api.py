from flask import Blueprint, jsonify
from dateutil.parser import parse

from download_transcribe_processor import DownloadAndTranscribeProcessor
from downloads import DownloadQueue
from reports.pandoc_report_generator import PandocReportGenerator
from reports.report_time_span_defn import ReportTimeSpanDefn
from rss_feed_scanner import RssFeedScanner
from summarization import SummarizeQueue
from summarize_queue_processor import SummarizeQueueProcessor

api_bp = Blueprint('api', __name__)

download_csv_cache = ""
downloaded_csv_cache = ""
summarized_csv_cache = ""
summarize_queue_csv_cache = ""
rssList = None
downloadPath = ""
outputPath = ""
singleton_process_all_running = False

def define_cache_files(download_csv, downloaded_csv, summarize_csv, summarized_csv):
    global download_csv_cache, downloaded_csv_cache, summarize_queue_csv_cache, summarized_csv_cache

    download_csv_cache= download_csv
    downloaded_csv_cache = downloaded_csv
    summarize_queue_csv_cache = summarize_csv
    summarized_csv_cache = summarized_csv


def define_paths(download_path, output_path):
    global downloadPath, outputPath
    downloadPath = download_path
    outputPath = output_path

def define_rssList(rss_list):
    global rssList
    rssList = rss_list

@api_bp.route('/processall', methods=['POST'])
def post_process_all():

    global singleton_process_all_running

    if singleton_process_all_running:
        print("already processing all")
        return jsonify({"message": "Already Running Process All"}), 200

    singleton_process_all_running = True
    download_queue = DownloadQueue(download_csv_cache, downloaded_csv_cache)

    # get the summarize queue
    summarize_queue = SummarizeQueue(summarize_queue_csv_cache, summarized_csv_cache)

    feed_scanner = RssFeedScanner(outputPath, download_queue, rssList, downloadPath)
    feed_scanner.scan_for_new_podcasts()

    download_queue_processor = DownloadAndTranscribeProcessor(download_queue, summarize_queue, downloadPath, outputPath)
    download_queue_processor.download_transcribe_and_queue_for_summarization()

    summarize_processor = SummarizeQueueProcessor(summarize_queue, outputPath, rssList.feeds)
    summarize_processor.summarize_all()

    # TODO: auto build the summary pdfs by category and date range config
    report_defns = [
        ReportTimeSpanDefn("output-reports/2025-07-july", "2025-07-01 00:00:01 UTC", "2025-07-31 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-07-july/july-01-07", "2025-07-01 00:00:01 UTC","2025-07-07 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-07-july/july-08-15", "2025-07-08 00:00:01 UTC","2025-07-15 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-07-july/july-16-23", "2025-07-16 00:00:01 UTC","2025-07-23 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-07-july/july-24-31", "2025-07-24 00:00:01 UTC","2025-07-31 23:59:59 UTC")
    ]

    for a_report_timespan in report_defns:
        # outputReportFolderName = "output-reports/2025-07-july"
        # fromDate = parse("2025-07-01 00:00:01 UTC")
        # toDate = parse("2025-07-31 23:59:59 UTC")
        print(f"Generating {a_report_timespan.output_folder} - {a_report_timespan.from_date} to {a_report_timespan.to_date}")

        outputReportFolderName = a_report_timespan.output_folder
        fromDate = parse(a_report_timespan.from_date)
        toDate = parse(a_report_timespan.to_date)

        #todo: create reports based on categories e.g. testing, ai, etc. (this needs to be defined at a podcast feed meta-data level on podcastname)
        #podcast_names_to_exclude = ["MLOps.community","Technovation", "Fastlane Founders"]

        reporter = PandocReportGenerator(outputPath, outputReportFolderName)
        reporter.generate_reports_for(fromDate, toDate, "testing", [], ["testing"], rssList.feeds)
        reporter.generate_reports_for(fromDate, toDate, "ai", [], ["ai"], rssList.feeds)
        reporter.generate_reports_for(fromDate, toDate, "business_marketing", [], ["business","marketing"], rssList.feeds)

    singleton_process_all_running = False

    return jsonify({"message": "Processed Everything"}), 200