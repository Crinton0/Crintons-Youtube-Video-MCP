from fastmcp import FastMCP

import os
import subprocess
import json

mcp = FastMCP("Youtube Videos API")


from youtube_transcript_api import YouTubeTranscriptApi

PREFERRED_TRANSCRIPTS = ["en", "en-US", "fr", "ru", "es", "ja", "de", "zh"]


@mcp.tool
def get_text_transcript(id: str) -> str:
        """
        Returns the text of the transcript of the youtube video, if available.

        Parameters:
        id: ID of a youtube video
        """
        response = ""

        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(id, languages=PREFERRED_TRANSCRIPTS)

        for snippet in transcript:
            response += snippet.text + " "

        return response



@mcp.tool
def get_metadata(video_link: str) -> str:
        """
        Given a link, it downloads, parses and returns metadata regarding the video.

        Parameters:
        video_link: Full link of the youtube video

        Returns:
        Title, description, duration, view count, like count, channel, channel follower count, upload date
        """
        response = ""
        
        metadata = {
            "title" : "",
            "description" : "",
            "duration" : "",
            "view_count" : "",
            "like_count" : "",
            "channel" : "",
            "channel_follower_count" : "",
            "upload_date" : ""
        }


        # Plan: execute yt-dlp, pass --skip-download or whatever, --write-info-json
        # Then, read the json into python. Collect only important fields like video name,
        # channel name, description and so on
        get_filename_process = subprocess.Popen(['yt-dlp', video_link, '--skip-download', '--print', 'filename'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = get_filename_process.communicate()

        filename_clean = out.strip()
        filename_noext, _ = os.path.splitext(filename_clean)
        filename_infojson = filename_noext + ".info.json"
        

        #yt-dlp 'https://youtu.be/j2dr04ejUHw?si=gy6f2kSb_IELe0GJ' --write-info-json --skip-download
        download_process = subprocess.call(['yt-dlp', video_link, '--skip-download', '--write-info-json']) # Downloads and creates a file

        with open(filename_infojson, "r") as file:
            file_json = json.load(file)

            metadata["title"] = file_json["title"]
            metadata["description"] = file_json["description"]
            metadata["duration"] = str(file_json["duration_string"])
            metadata["view_count"] = str(file_json["view_count"])
            metadata["like_count"] = str(file_json["like_count"])
            metadata["channel"] = file_json["channel"]
            metadata["channel_follower_count"] = str(file_json["channel_follower_count"])
            metadata["upload_date"] = file_json["upload_date"]


            subprocess.call(['rm', '-rf', filename_infojson]) # Downloads and creates a file
            print("Deleted " + filename_infojson)
            

        
        return response + json.dumps(metadata, indent=4)



if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
