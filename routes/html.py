from flask import Blueprint, render_template_string, render_template

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
    return render_template_string('''
    <h1>RSS Feeds</h1>
    <ul>
        {% for feed in feeds %}
            <li>{{ feed.feedname }} - {{ feed.feed_rss_url }}</li>
        {% endfor %}
    </ul>
    ''', feeds=feeds)