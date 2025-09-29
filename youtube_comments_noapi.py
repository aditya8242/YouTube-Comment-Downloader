#!/usr/bin/env python3
import argparse
import json
import csv
import webbrowser
import re
import requests
from pathlib import Path
from youtube_comment_downloader import YoutubeCommentDownloader

def sanitize_filename(name: str) -> str:
    """Remove illegal characters for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_video_title(url: str) -> str:
    """Fetch video title from YouTube page source."""
    try:
        html = requests.get(url, timeout=10).text
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group(1).replace("- YouTube", "").strip()
            return sanitize_filename(title)
    except Exception as e:
        print(f"[!] Could not fetch title: {e}")
    return "youtube_video"

def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from different URL formats.
    Supports:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    - https://www.youtube.com/shorts/VIDEOID
    """
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})"
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None

def download_comments(url, limit=None):
    """Download comments from YouTube video."""
    downloader = YoutubeCommentDownloader()
    comments_iter = downloader.get_comments_from_url(url)

    comments = []
    for i, c in enumerate(comments_iter, 1):
        comments.append({
            "id": c.get("comment_id"),
            "author": c.get("author"),
            "text": c.get("text"),
            "likeCount": c.get("votes"),
            "publishedAt": c.get("time")
        })
        if limit and i >= limit:
            break
    return comments

def save_json(comments, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {len(comments)} comments to {filename}")

def save_csv(comments, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "author", "text", "likeCount", "publishedAt"])
        writer.writeheader()
        writer.writerows(comments)
    print(f"[+] Saved {len(comments)} comments to {filename}")

def save_html(comments, filename, title, video_id, url):
    # Only embed for standard watch URLs, not shorts or unsupported formats
    if video_id and "shorts" not in url:
        iframe_src = f"https://www.youtube.com/embed/{video_id}?rel=0&autoplay=0"
        iframe_html = f'<iframe src="{iframe_src}" allowfullscreen></iframe>'
    else:
        iframe_html = ''  # no embed for shorts/restricted

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{title} - YouTube Comments</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f9f9f9;
                padding: 20px;
                transition: background 0.3s, color 0.3s;
            }}
            body.dark-mode {{
                background: #1e1e1e;
                color: #e0e0e0;
            }}
            .search-box {{ margin-bottom: 20px; }}
            .comment {{
                background: #fff;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            body.dark-mode .comment {{
                background: #2a2a2a;
                box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            }}
            .author {{ font-weight: bold; }}
            .meta {{ font-size: 0.9em; color: #555; }}
            body.dark-mode .meta {{ color: #aaa; }}
            button {{ margin-left: 10px; }}
            iframe {{
                width: 560px;
                height: 315px;
                border: none;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>{title} - Comments Viewer (💬 {len(comments)} comments)</h1>
        <p><a href="{url}" target="_blank">Watch on YouTube</a></p>
        {iframe_html}
        <br>
        <input class="search-box" type="text" id="search" placeholder="Search comments..." onkeyup="filterComments()">
        <select id="sort" onchange="sortComments()">
            <option value="default">Sort by Default</option>
            <option value="likes">Sort by Likes</option>
            <option value="newest">Sort by Newest</option>
            <option value="oldest">Sort by Oldest</option>
        </select>
        <button onclick="toggleTheme()">Toggle Light/Dark</button>
        <div id="comments"></div>

        <script>
            const comments = {json.dumps(comments, ensure_ascii=False)};
            const container = document.getElementById("comments");

            function render(list) {{
                container.innerHTML = "";
                list.forEach(c => {{
                    const div = document.createElement("div");
                    div.className = "comment";
                    div.innerHTML = `<div class="author">${{c.author}}</div>
                                     <div class="meta">${{c.publishedAt}} · 👍 ${{c.likeCount}}</div>
                                     <div class="text">${{c.text}}</div>`;
                    container.appendChild(div);
                }});
            }}

            function filterComments() {{
                const q = document.getElementById("search").value.toLowerCase();
                const filtered = comments.filter(c => 
                    c.text.toLowerCase().includes(q) || 
                    (c.author && c.author.toLowerCase().includes(q))
                );
                render(filtered);
            }}

            function sortComments() {{
                const option = document.getElementById("sort").value;
                let sorted = [...comments];
                if (option === "likes") {{
                    sorted.sort((a,b) => (b.likeCount || 0) - (a.likeCount || 0));
                }} else if (option === "newest") {{
                    sorted.sort((a,b) => new Date(b.publishedAt) - new Date(a.publishedAt));
                }} else if (option === "oldest") {{
                    sorted.sort((a,b) => new Date(a.publishedAt) - new Date(b.publishedAt));
                }}
                render(sorted);
            }}

            function toggleTheme() {{
                document.body.classList.toggle("dark-mode");
            }}

            render(comments);
        </script>
    </body>
    </html>
    """
    Path(filename).write_text(html_content, encoding="utf-8")
    print(f"[+] Saved {len(comments)} comments to {filename}")
    webbrowser.open("file://" + str(Path(filename).resolve()))

def main():
    parser = argparse.ArgumentParser(description="Download YouTube comments without API")
    parser.add_argument("-u", "--url", help="YouTube video URL")
    parser.add_argument("-o", "--output", default=None, help="Base output filename (no extension)")
    parser.add_argument("-n", "--number", type=int, default=None, help="Limit number of comments (optional)")
    args = parser.parse_args()

    url = args.url or input("Enter YouTube video URL: ").strip()
    video_id = extract_video_id(url)
    title = get_video_title(url)
    comments = download_comments(url, limit=args.number)

    if not comments:
        print("[-] No comments found.")
        return

    base_name = args.output or title
    save_json(comments, f"{base_name}.json")
    save_csv(comments, f"{base_name}.csv")
    save_html(comments, f"{base_name}.html", title, video_id, url)

if __name__ == "__main__":
    main()
