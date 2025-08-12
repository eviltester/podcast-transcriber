import os

from flask import Blueprint, jsonify
from dateutil.parser import parse

from download_transcribe_processor import DownloadAndTranscribeProcessor
from downloads import DownloadQueue, filenameify
from markdownReporter import generateMarkdownSummaryReport
from reports.pandoc_report_generator import PandocReportGenerator
from reports.report_time_span_defn import ReportTimeSpanDefn
from rss_feed_scanner import RssFeedScanner
from summarise_using_ollama import summarizeTranscriptFile, adhoc_summary
from summarization import SummarizeQueue
from summarize_queue_processor import SummarizeQueueProcessor

api_bp = Blueprint('api', __name__)

rssList = None
singleton_process_all_running = False

def define_rssList(rss_list):
    global rssList
    rssList = rss_list

@api_bp.route('/regeneratesummary/<podcast_path>/<episode_path>', methods=['POST'])
def post_regenerate_episode_summary(podcast_path, episode_path):
    fileToRead = os.path.join(rssList.output_path, filenameify(podcast_path), filenameify(episode_path), filenameify(episode_path) + "-base.para.md")
    if os.path.exists(fileToRead):
        summarizeTranscriptFile(fileToRead)
        generateMarkdownSummaryReport(rssList.output_path, podcast_path, episode_path, rssList.get_podcast_details(podcast_path))
        return jsonify({"message": "Regenerated Summary"}), 200
    else:
        return jsonify({"message": f"Could not find episode to regenerate {fileToRead}"}), 404

@api_bp.route('/regeneratemarkdownsummary/<podcast_path>/<episode_path>', methods=['POST'])
def post_regenerate_episode_markdown_summary(podcast_path, episode_path):
    fileToRead = os.path.join(rssList.output_path, filenameify(podcast_path), filenameify(episode_path), filenameify(episode_path) + "-base.para.md")
    if os.path.exists(fileToRead):
        generateMarkdownSummaryReport(rssList.output_path, podcast_path, episode_path, rssList.get_podcast_details(podcast_path))
        return jsonify({"message": "Regenerated Markdown Summary"}), 200
    else:
        return jsonify({"message": f"Could not find episode to regenerate {fileToRead}"}), 404

@api_bp.route('/regeneratesummarytype/<summary_type>/<podcast_path>/<episode_path>', methods=['POST'])
def post_regenerate_summary(summary_type,podcast_path, episode_path):
    summary_path = os.path.join(rssList.output_path, filenameify(podcast_path), filenameify(episode_path), "intermediate-summary.md")
    if os.path.exists(summary_path):
        adhoc_summary(os.path.dirname(summary_path), [summary_type])
        return jsonify({"message": f"Regenerated {summary_type} Summary"}), 200
    else:
        return jsonify({"message": f"Could not find episode with intermediate summary to regenerate {summary_path}"}), 404

@api_bp.route('/processall', methods=['POST'])
def post_process_all():

    global singleton_process_all_running
    global rssList

    if singleton_process_all_running:
        print("already processing all")
        return jsonify({"message": "Already Running Process All"}), 200

    if rssList is None:
        print("Rss List is not configured")
        return jsonify({"message": "Rss List Not Configured"}), 428

    singleton_process_all_running = True

    try:
        download_queue = DownloadQueue(rssList.download_csv_cache, rssList.downloaded_csv_cache)

        # get the summarize queue
        summarize_queue = SummarizeQueue(rssList.summarize_queue_csv_cache, rssList.summarized_csv_cache)

        feed_scanner = RssFeedScanner(rssList.output_path, download_queue, rssList, rssList.download_path)
        feed_scanner.scan_for_new_podcasts()

        download_queue_processor = DownloadAndTranscribeProcessor(download_queue, summarize_queue, rssList.download_path, rssList.output_path)
        download_queue_processor.download_transcribe_and_queue_for_summarization()

        summarize_processor = SummarizeQueueProcessor(summarize_queue, rssList.output_path, rssList.feeds)
        summarize_processor.summarize_all()

    finally:
        singleton_process_all_running = False

    return jsonify({"message": "Processed Everything"}), 200

@api_bp.route('/generate-all-markdown-reports', methods=['POST'])
def auto_gen_markdown_reports():
    # TODO: auto build the summary pdfs by category and date range config supplied in a specific API call from UI
    report_defns = [
        ReportTimeSpanDefn("output-reports/2025-08-august", "2025-08-01 00:00:01 UTC", "2025-08-31 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-08-august/august-01-07", "2025-08-01 00:00:01 UTC","2025-08-07 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-08-august/august-08-15", "2025-08-08 00:00:01 UTC","2025-08-15 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-08-august/august-16-23", "2025-08-16 00:00:01 UTC","2025-08-23 23:59:59 UTC"),
        ReportTimeSpanDefn("output-reports/2025-08-august/august-24-31", "2025-08-24 00:00:01 UTC","2025-08-31 23:59:59 UTC")
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

        reporter = PandocReportGenerator(rssList.output_path, outputReportFolderName)
        reporter.generate_reports_for(fromDate, toDate, "testing", [], ["testing"], rssList.feeds)
        reporter.generate_reports_for(fromDate, toDate, "ai_dev", [], ["ai","development"], rssList.feeds)
        reporter.generate_reports_for(fromDate, toDate, "business_marketing", [], ["business","marketing"], rssList.feeds)

    return jsonify({"message": "Reports Generated"}), 200