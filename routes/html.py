import fnmatch
import os
import io
from ollama import generate
from pathlib import Path
from flask import Blueprint, request, render_template_string, render_template

from downloads import filenameify
from podcast_episode import load_the_podcast_episode_data_from_file, load_the_podcast_episode_data
from rss import RssFeed
from markdown_it import MarkdownIt

from summarization import SummarizeQueue

html_bp = Blueprint('html', __name__)

feeds = []
output_path = None
podcasts_path = None

def set_feeds_list(list_of_feeds):
    global feeds
    feeds = list_of_feeds


def set_output_report_path(a_path):
    global output_path
    output_path = a_path

def set_podcast_folders_path(a_path):
    global podcasts_path
    podcasts_path = a_path


def set_cache_files(download_csv, downloaded_csv, summarize_csv, summarized_csv):
    global download_csv_cache, downloaded_csv_cache, summarize_queue_csv_cache, summarized_csv_cache

    download_csv_cache= download_csv
    downloaded_csv_cache = downloaded_csv
    summarize_queue_csv_cache = summarize_csv
    summarized_csv_cache = summarized_csv

def get_feeds_list():
    return sorted(feeds,key=lambda feed: feed.feedname)

def get_recent_episodes():

    recent_episodes = {}

    summarize_queue = SummarizeQueue(summarize_queue_csv_cache, summarized_csv_cache)

    # this approach doesn't work if we have just added a new podcast, we should really scan all episodes and get the most recent
    done_count = len(summarize_queue.done)
    recent_limit = done_count-30
    while done_count > recent_limit:

        done_count = done_count-1
        a_recent_episode = summarize_queue.done[done_count]
        an_episode = load_the_podcast_episode_data(podcasts_path, a_recent_episode.podcast_name, a_recent_episode.episode_title)
        if an_episode != None:
            recent_episodes[filenameify(a_recent_episode.podcast_name) + "/" + filenameify(a_recent_episode.episode_title)] = an_episode

    return recent_episodes


def find_pdf_files(directory):
    pdf_files = []

    for root, dirs, files in os.walk(directory):
        # Filter files to include only those ending with '.pdf'
        pdf_files.extend(os.path.join(root, file) for file in fnmatch.filter(files, '*.pdf'))

    return pdf_files

def generate_html_list(pdf_files, parent_dir):

    print(pdf_files)

    html = "<ul>\n"

    for a_file in pdf_files:
        output_name = a_file.replace(parent_dir,"")
        html += f"<li><a href='file:///{a_file}'>{output_name}</a></li>"
    html += "</ul>"

    return html



@html_bp.route('/', methods=['GET'])
def index():
    pdf_files = find_pdf_files(output_path)
    # local files do not link
    #pdf_output_files_html = generate_html_list(pdf_files, output_path)
    #print(pdf_output_files_html)

    # TODO: use summarized_items.csv to find the last x0 summarized podcasts and list on screen, sorted by published date
    recent_episodes = get_recent_episodes()
    recent_episodes_html = get_episode_list_html(recent_episodes, True)

    return render_template('index.html', html_list="", recent_episodes_html = recent_episodes_html)

@html_bp.route('/ollamaexec', methods=['GET','POST'])
def post_process_with_ollama():
    if request.method == 'POST':
        modelname = request.form['modelname'].strip()
        file = request.files['filepath']
        filename = file.filename
        filecontent = io.StringIO(file.read().decode('utf-8')).getvalue()
        prompt = request.form['prompt']

        given_number_of_times_to_repeat_prompt = int(request.form['repeat'].strip())
        number_of_times_to_repeat_prompt = given_number_of_times_to_repeat_prompt

        responses = []
        send_prompt = f"{prompt} {filecontent}"

        while number_of_times_to_repeat_prompt > 0:
            response = generate(model=modelname, prompt=send_prompt)
            responses.append(response)
            number_of_times_to_repeat_prompt -= 1

        response_html = f"<p>done {modelname} {filename}</p><p>{prompt}</p>"

        for aresponse in responses:
            response_html += f"\n<hr/><div><pre>{aresponse.response}</pre></div>"

        return render_template(
            'ollama.html',
            response_html=response_html,
            given_modelname = modelname,
            given_prompt = prompt,
            given_repeat_number = given_number_of_times_to_repeat_prompt
        )
    return render_template('ollama.html')

@html_bp.route('/podcasts', methods=['GET'])
def get_podcasts():
    feeds = get_feeds_list()
    return render_template('podcasts.html', feeds=feeds)


def get_episode_list_html(episodes, include_podcast_name):
    html = "<ul>"

    # sort by date reversed order
    for key in sorted(episodes, key = lambda name: episodes[name].published, reverse=True):
        value = episodes[key]
        podcast_name = ""
        if include_podcast_name:
            podcast_name = value.podcastName + " - "
        html += f"<li>{podcast_name} <a href='/episode/{key}'>{value.title}</a> - {value.published} ({value.duration})</li>"
    html += "</ul>"

    return html

@html_bp.route('/podcasts/<name>', methods=['GET'])
def get_podcast(name):
    feed = None
    for feed in get_feeds_list():
        if feed.url_safe_feedname == name:
            break

    message_html = ""

    if feed != None:
        # load in all folder names and the episodes
        podcast_episodes_folder = os.path.join(podcasts_path, feed.url_safe_feedname)

        episodes = {}
        if os.path.exists(podcast_episodes_folder):
            files = os.listdir(podcast_episodes_folder)
            for a_file in files:
                if os.path.isdir(os.path.join(podcast_episodes_folder, a_file)):
                    an_episode = load_the_podcast_episode_data(podcasts_path, name, os.path.basename(a_file))
                    if an_episode != None:
                        episodes[feed.url_safe_feedname + "/" + os.path.basename(a_file)] = an_episode
        else:
            message_html = "<p>Podcast not found on disk. Perhaps it is still processing?"

    episode_list = get_episode_list_html(episodes, False)

    return render_template('podcast.html', feed=feed, episode_list=episode_list, message_html= message_html)

@html_bp.route('/episode/<podcastname>/<episodetitle>', methods=['GET'])
def get_episode(podcastname, episodetitle):

    an_episode = load_the_podcast_episode_data(podcasts_path, podcastname, episodetitle)

    md = MarkdownIt()

    episode_summary_html = md.render(an_episode.summary)

    summary_html=""
    summary_path = os.path.join(podcasts_path, podcastname, episodetitle, "summary-" + episodetitle + ".md")
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as file:
            summary_md = file.read()

        summary_html = md.render(summary_md)

    transcript_path = os.path.join(podcasts_path, podcastname, episodetitle, episodetitle + "-base.para.md")

    transcript_html=""
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r') as file:
            transcript_md = file.read()
        transcript_html = md.render(transcript_md)

    return render_template(
        'episode.html',
        episode=an_episode,
        official_summary=episode_summary_html,
        summary_html=summary_html,
        transcript_html=transcript_html,
        podcast_path= podcastname
    )