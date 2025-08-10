import fnmatch
import os
import io
from ollama import generate
from flask import Blueprint, request, render_template

from downloads import filenameify
from podcast_episode import load_the_podcast_episode_data
from markdown_it import MarkdownIt

from summarization import SummarizeQueue

html_bp = Blueprint('html', __name__)

rss_list = None
feeds = []
report_output_path = None
podcasts_path = None

def set_rsslist(an_rss_list):
    global rss_list
    rss_list = an_rss_list

    set_feeds_list(rss_list.feeds)
    set_output_report_path(os.path.join(rss_list.output_path, "output-reports"))
    set_podcast_folders_path(rss_list.output_path)

def set_feeds_list(list_of_feeds):
    global feeds
    feeds = list_of_feeds

def set_output_report_path(a_path):
    global report_output_path
    report_output_path = a_path

def set_podcast_folders_path(a_path):
    global podcasts_path
    podcasts_path = a_path


def get_feeds_list():
    return sorted(feeds,key=lambda feed: feed.feedname)

def get_recent_episodes(for_category=None):

    recent_episodes = {}

    # TODO: share the same queue
    summarize_queue = SummarizeQueue(rss_list.summarize_queue_csv_cache, rss_list.summarized_csv_cache)

    # this approach doesn't work if we have just added a new podcast, we should really scan all episodes and get the most recent
    done_count = len(summarize_queue.done)
    # show max 30 most recent
    recent_limit = 30
    while recent_limit > 0 and done_count>=0:

        done_count = done_count-1
        a_recent_episode = summarize_queue.done[done_count]
        an_episode = load_the_podcast_episode_data(podcasts_path, a_recent_episode.podcast_name, a_recent_episode.episode_title)
        podcast_in_list = rss_list.get_podcast_details(a_recent_episode.podcast_name)
        if an_episode is not None and podcast_in_list is not None:

            include_podcast_episode = True

            if for_category is not None and for_category not in podcast_in_list.categories:
                include_podcast_episode = False

            if include_podcast_episode:
                recent_episodes[filenameify(a_recent_episode.podcast_name) + "/" + filenameify(a_recent_episode.episode_title)] = an_episode
                recent_limit = recent_limit-1

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
    pdf_files = find_pdf_files(report_output_path)
    # local files do not link
    #pdf_output_files_html = generate_html_list(pdf_files, report_output_path)
    #print(pdf_output_files_html)

    # TODO: use summarized_items.csv to find the last x0 summarized podcasts and list on screen, sorted by published date
    recent_episodes = get_recent_episodes()
    recent_episodes_html = get_episode_list_html(recent_episodes, True)

    return render_template('index.html', html_list="", recent_episodes_html = recent_episodes_html)

@html_bp.route('/ollamaexec', methods=['GET','POST'])
def post_process_with_ollama():
    if request.method == 'POST':
        modelname = request.form['modelname'].strip()
        given_suffix = request.form['suffix'].strip()
        file = request.files['filepath']
        filename = file.filename
        filecontent = io.StringIO(file.read().decode('utf-8')).getvalue()
        prompt = request.form['prompt']

        system_prompt = request.form['system'].strip()

        given_systemprompt = None
        if len(system_prompt) > 0:
            given_systemprompt = system_prompt

        given_number_of_times_to_repeat_prompt = int(request.form['repeat'].strip())
        number_of_times_to_repeat_prompt = given_number_of_times_to_repeat_prompt

        responses = []

        given_options = request.form['options'].strip()
        options_to_parse = given_options.split("\n")
        options_as_dict = {}
        for an_option in options_to_parse:
            name_value = an_option.split("=")
            if len(name_value) >= 2:
                a_name = name_value[0].strip()
                a_value = name_value[1].strip()
                if len(a_name) > 0 and len(a_value) > 0:
                    options_as_dict[a_name] = a_value

        if len(options_as_dict) == 0:
            options_as_dict = None

        filecontent_output = filecontent
        if len(filecontent)>50:
            filecontent_output = f"{filecontent[0:50]}..."

        print(f"{prompt} {filecontent_output}")

        send_prompt = f"{prompt} {filecontent}"

        # https://github.com/ollama/ollama-python/blob/main/ollama/_client.py
        # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
        # https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune#official-recommended-settings

        while number_of_times_to_repeat_prompt > 0:
            response = generate(
                model=modelname,
                prompt=send_prompt,
                system = given_systemprompt,
                options = options_as_dict,
                suffix = given_suffix
            )
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
            given_repeat_number = given_number_of_times_to_repeat_prompt,
            given_systemprompt = system_prompt,
            given_options = given_options,
            given_suffix = given_suffix
        )

    else:
        return render_template('ollama.html')

@html_bp.route('/podcasts', methods=['GET'])
def get_podcasts():
    categories = []
    if not rss_list is None:
        categories = rss_list.get_category_names()

    feeds = get_feeds_list()
    return render_template('podcasts.html', feeds=feeds, categories = categories)


def feeds_list_as_markdown(feedslist):
    md = ""
    for a_feed in feedslist:
        md += f"- {a_feed.feedname}\n"
        md += f"    - [{a_feed.homeUrl}]({a_feed.homeUrl})\n"
        md += f"    - {a_feed.description}\n"
    return md

@html_bp.route('/category/<category_name>', methods=['GET'])
def get_category_podcasts(category_name):
    categories = []
    if not rss_list is None:
        categories = rss_list.get_category_names()

    feeds = get_feeds_list()
    filtered_feeds = list(filter(lambda feed: category_name.lower() in feed.categories, feeds))

    pres = []
    # output markdown to log
    if not request.args.get('markdown') is None:
        pres.append(feeds_list_as_markdown(filtered_feeds))

    names = ""
    for a_feed in filtered_feeds:
        names += f"- {a_feed.feedname}\n"

    if not request.args.get('markdown') is None:
        pres.append(names)

    recent_episodes = get_recent_episodes(for_category=category_name)
    recent_episodes_html = get_episode_list_html(recent_episodes, True)

    return render_template(
        'podcasts.html',
        feeds=filtered_feeds,
        categories = categories,
        category_name = category_name.capitalize(),
        pres = pres,
        recent_episodes_html = recent_episodes_html
    )

def get_episode_list_html(episodes, include_podcast_name):
    html = "<ul>"

    # sort by date reversed order
    for key in sorted(episodes, key = lambda name: episodes[name].published, reverse=True):
        value = episodes[key]
        podcast_name = ""
        if include_podcast_name:
            podcast_name = value.podcastName + " - "
        html += f"<li>{podcast_name} <a href='/episode/{key}'>{value.title}</a> - {value.published} ({value.duration})"
        if value.one_para_generated_summary != "":
            html += f"<ul><li>{value.one_para_generated_summary}</li></ul>"
        html += "</li>"
    html += "</ul>"

    return html

@html_bp.route('/podcasts/<name>', methods=['GET'])
def get_podcast(name):

    feed = None
    if not rss_list is None:
        feed = rss_list.get_podcast_details(name)

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

    feed = None
    if not rss_list is None:
        feed = rss_list.get_podcast_details(podcastname)

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
        podcast_path= podcastname,
        episode_path = episodetitle,
        feed = feed
    )