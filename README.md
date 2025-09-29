# YouTube-Comment-Downloader (No API)

A simple Python tool to download YouTube comments without using the official API.
It saves comments in JSON, CSV, and interactive HTML, with a light/dark theme toggle, search, and sort features.

---

# Features

- Download comments without YouTube API or keys.  
- Interactive HTML viewer:  
  - Search comments in real-time  
  - Sort by likes, newest, oldest  
  - Light/Dark theme toggle  
  - Comment count badge  
- HTML includes clickable link to the video and embedded player (works for standard videos, not all shorts).  
- Output files are named after the YouTube video title:  
  - `Video Title.json`  
  - `Video Title.csv`  
  - `Video Title.html` (opens automatically in your browser)

---

# Installation

1. Clone or download this repository.  
2. Install dependencies from `requirements.txt`:
```
pip install -r requirements.txt
```

---

# Usage
Run the script:
```
python youtube_comments_noapi.py -u "YOUTUBE_VIDEO_URL"
```
Or run without -u to input URL interactively:
```
python youtube_comments_noapi.py
```

Optional arguments:

- -o OUTPUT → set custom base filename (default: video title)
- -n NUMBER → limit number of comments to download
```
python youtube_comments_noapi.py -u "YOUTUBE_VIDEO_URL" -n 200
```

# Notes/Limitations
- There is no loading animation, so fetching large numbers of comments may take some time. Please be patient.
- Embedded video may not work for some Shorts, age-restricted, private, or region-restricted videos. In all cases, the clickable link is available.
- Works best with standard public YouTube videos.

---

# HTML Features

- Search box: filter comments by author or text.
- Sort dropdown: sort comments by likes, newest, or oldest.
- Light/Dark toggle: click the button to switch themes.
- Comment count: displayed in the header (💬 1342 comments).
- Video embed: plays the video directly if supported.

---

# How it works

1. Downloads comments using youtube-comment-downloader.
2. Fetches video title by scraping the page (no API used).
3. Saves outputs as JSON, CSV, and interactive HTML.
4. HTML file opens automatically in your default browser.

---

# Tips

- Test with small comment limits first (-n 50) to check behavior.
- Always check the HTML in a browser; large comment lists may take a few seconds to render.
- Use this tool responsibly; YouTube may change their page structure, which could break scraping.

---

# Disclaimer

This tool/project is made entirely using ChatGPT.
This is entirely "vibe coding". From all the code till documentation. (except for this disclaimer, as AI tools don't know what "vibe coding" is.)
I made it because sometimes the YouTube UI feels so overwhelming that I decided to keep only a small embeded video and comments.
