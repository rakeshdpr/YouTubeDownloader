import os
import subprocess
import shutil
import re
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Check yt-dlp and ffmpeg availability
if not shutil.which("yt-dlp"):
    raise RuntimeError("yt-dlp is not installed or not in PATH.")
if not shutil.which("ffmpeg"):
    raise RuntimeError("ffmpeg is not installed or not in PATH.")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/formats", methods=["POST"])
def list_formats():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Run yt-dlp --list-formats and capture output
        result = subprocess.run(
            ["yt-dlp", "--list-formats", url],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        formats_text = result.stdout

        # Parse formats lines that have format id, extension, resolution, and type
        formats = []
        for line in formats_text.splitlines():
            # Regex to capture format id, extension, resolution, note (video/audio info)
            m = re.match(r"^(\d+)\s+(\w+)\s+([\dxp]+)\s+(.*)$", line)
            if m:
                fmt_id, ext, res, note = m.groups()
                # Determine type
                if "video only" in note:
                    fmt_type = "Video Only"
                elif "audio only" in note:
                    fmt_type = "Audio Only"
                else:
                    fmt_type = "Video+Audio"
                formats.append({
                    "id": fmt_id,
                    "ext": ext,
                    "resolution": res,
                    "type": fmt_type,
                    "note": note.strip()
                })

        if not formats:
            return jsonify({"error": "No formats found"}), 404

        return jsonify({"formats": formats})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to fetch formats: {e.stderr}"}), 500


@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")
    format_id = data.get("format_id")
    format_type = data.get("format_type")

    if not url or not format_id or not format_type:
        return jsonify({"error": "Missing parameters"}), 400

    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")
    # Build format string for yt-dlp:
    # If video only, merge with best audio automatically
    if format_type == "Video Only":
        fmt_str = f"{format_id}+bestaudio"
    else:
        fmt_str = format_id

    try:
        subprocess.run(
            [
                "yt-dlp",
                "-f",
                fmt_str,
                "--merge-output-format",
                "mp4",
                "-o",
                output_template,
                url,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Download failed: {e.stderr}"}), 500

    # Find the downloaded file path (the latest mp4 in downloads)
    files = [
        f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".mp4")
    ]
    if not files:
        return jsonify({"error": "Downloaded file not found"}), 500
    latest_file = max(
        files, key=lambda f: os.path.getctime(os.path.join(DOWNLOAD_FOLDER, f))
    )

    return jsonify({"filename": latest_file})


@app.route("/download_file/<filename>")
def serve_file(filename):
    # Serve the downloaded file for user to download
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
