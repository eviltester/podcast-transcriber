import fnmatch
import os
from pathlib import Path

from flask import Blueprint, render_template_string, render_template

from podcast_episode import load_the_podcast_episode_data_from_file, load_the_podcast_episode_data
from rss import RssFeed

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

def get_feeds_list():
    return feeds


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
    return render_template('index.html', html_list="")


@html_bp.route('/podcasts', methods=['GET'])
def get_podcasts():
    feeds = get_feeds_list()
    return render_template('podcasts.html', feeds=feeds)


def get_episode_list_html(episodes):
    html = "<ul>"

    for key, value in episodes.items():
        html += f"<li><a href='/episode/{key}'>{value.title}</a></li>"
    html += "</ul>"

    return html

@html_bp.route('/podcasts/<name>', methods=['GET'])
def get_podcast(name):
    feed = None
    for feed in get_feeds_list():
        if feed.url_safe_feedname == name:
            break

    if feed != None:
        # load in all folder names and the episodes
        podcast_episodes_folder = os.path.join(podcasts_path, feed.url_safe_feedname)
        episodes = {}
        files = os.listdir(podcast_episodes_folder)
        for a_file in files:
            if os.path.isdir(os.path.join(podcast_episodes_folder, a_file)):
                an_episode = load_the_podcast_episode_data(podcasts_path, name, os.path.basename(a_file))
                if an_episode != None:
                    episodes[feed.url_safe_feedname + "/" + os.path.basename(a_file)] = an_episode


    episode_list = get_episode_list_html(episodes)

    return render_template('podcast.html', feed=feed, episode_list=episode_list)

@html_bp.route('/episode/<podcastname>/<episodetitle>', methods=['GET'])
def get_episode(podcastname, episodetitle):

    an_episode = load_the_podcast_episode_data(podcasts_path, podcastname, episodetitle)
    return render_template('episode.html', episode=an_episode)