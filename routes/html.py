from flask import Blueprint, render_template_string, render_template

from rss import RssFeed

html_bp = Blueprint('html', __name__)

feeds = []

def set_feeds_list(list_of_feeds):
    global feeds
    feeds = list_of_feeds

def get_feeds_list():
    return feeds


@html_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@html_bp.route('/podcasts', methods=['GET'])
def get_podcasts():
    feeds = get_feeds_list()
    return render_template('podcasts.html', feeds=feeds)

@html_bp.route('/podcasts/<name>', methods=['GET'])
def get_podcast(name):
    feed = None
    for feed in get_feeds_list():
        if feed.url_safe_feedname == name:
            break

    return render_template('podcast.html', feed=feed)