import subprocess
import shutil
import os
import re
from typing import List, Dict, Any


def get_user_format_choice(max_choice: int) -> int:
    """Prompt user to choose a format index."""
    while True:
        try:
            choice = int(input(f"Enter the number of the quality you want to download (1-{max_choice}): "))
            if 1 <= choice <= max_choice:
                return choice
            else:
                print(f"Please enter a valid number between 1 and {max_choice}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def run_download(command: List[str]) -> None:
    """Run yt-dlp download command."""
    print("\nStarting download...")
    try:
        subprocess.run(command, check=True)
        print("\n✅ Download completed successfully!")
    except subprocess.CalledProcessError:
        print("\n❌ Error during download. Check output above.")
    except FileNotFoundError:
        print(f"\n❌ Command '{command[0]}' not found. Is it installed and in PATH?")


def download_high_quality_video(url: str, save_path: str = "./videos") -> None:
    """Download the chosen format from YouTube."""
    # Check prerequisites
    if not shutil.which("yt-dlp"):
        print("Error: 'yt-dlp' not found. Install with: pip install yt-dlp")
        return
    if not shutil.which("ffmpeg"):
        print("Error: 'ffmpeg' not found. Install FFmpeg and add to PATH.")
        return

    os.makedirs(save_path, exist_ok=True)

    # Get format list
    print(f"\nFetching available formats for: {url}")
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-formats", url],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        formats_text = result.stdout
    except subprocess.CalledProcessError as e:
        print("\n❌ Error fetching formats.")
        print(e.stderr)
        return

    # Parse formats with correct type detection
    available_formats: List[Dict[str, Any]] = []
    idx = 1
    for line in formats_text.splitlines():
        match = re.match(r"^(\d+)\s+(\w+)\s+(\d{3,4}x\d{3,4}|\d+p).*", line)
        if match:
            fmt_id, ext, res = match.groups()
            if "video only" in line:
                fmt_type = "Video Only"
            elif "audio only" in line:
                fmt_type = "Audio Only"
            else:
                fmt_type = "Video+Audio"
            available_formats.append({
                "index": idx,
                "id": fmt_id,
                "ext": ext,
                "res": res,
                "type": fmt_type
            })
            print(f"{idx}: {res} ({ext}) - {fmt_type} [ID: {fmt_id}]")
            idx += 1

    if not available_formats:
        print("No formats found.")
        return

    # Get choice
    choice = get_user_format_choice(len(available_formats))
    selected = next(f for f in available_formats if f["index"] == choice)

    print(f"\nYou selected: {selected['res']} - {selected['type']} (ID: {selected['id']})")

    # Build command
    if selected["type"] == "Video Only":
        fmt_selector = f"{selected['id']}+bestaudio"
    elif selected["type"] == "Audio Only":
        fmt_selector = selected["id"]
    else:
        fmt_selector = selected["id"]

    download_command = [
        "yt-dlp",
        "-f", fmt_selector,
        "--merge-output-format", "mp4",
        "-o", os.path.join(save_path, "%(title)s - %(resolution)s.%(ext)s"),
        url
    ]

    run_download(download_command)


if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ").strip()
    download_high_quality_video(video_url)
