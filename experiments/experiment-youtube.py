import os

import yt_dlp

from downloads import filenameify
from pathlib import Path

URLS = ['https://youtu.be/OeKxq-9WCo4']

ydl_opts = {
    'format': 'm4a/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    'paths': {  # Extract audio using ffmpeg
        'home': 'd:/downloads'
    },
    'windowsfilenames': True
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(URLS[0], download=False)
    output_filename = ydl.prepare_filename(info_dict)
    print(f"downloaded {output_filename}")
    error_code = ydl.download(URLS)
    output_file_path = Path(output_filename.replace(".mp4", ".m4a"))
    os.rename(output_filename.replace(".mp4", ".m4a"), os.path.join(output_file_path.parent, filenameify(URLS[0]) + ".m4a"))


print("done")