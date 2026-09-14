import os

import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")
SLACK_URL = os.environ.get("SLACK_WEBHOOK_URL")
URL = "https://www.googleapis.com/youtube/v3/channels"
IMAGE_URL = "https://yt3.ggpht.com/UdE3DnRdLAMfJa9vftMgvxRTAKuaNaA3uLnjdzkAxEqYDy2XmNHGF9CJninYMYijPxHpDZ_HJIs=s88-c-k-c0x00ffffff-no-rj"


def make_requests():
    response = None
    try:
        params = {
            "part": "statistics",
            "key": YOUTUBE_API_KEY,
            "id": YOUTUBE_CHANNEL_ID,
        }

        res = requests.get(url=URL, params=params)
        if not res.ok:
            print(
                f"API request failed due to {res.status_code} with message {res.json()}"
            )
            return
        response = res.json()
        return response
    except Exception as e:
        print(f"Error while making requests due to {e}")


def post_to_slack(response: dict[str, str]):
    attachment = None
    if not response:
        print("Response is None due to API failed or object is empty")
        attachment = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 YouTube Automation — API Error",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "*The YouTube API request did not return a valid response.*\n\n"
                            "🔴 *Status:* Request failed\n"
                            "📡 *Service:* YouTube Data API\n"
                            "⚙️ *Action:* Please check the API request and try again."
                        ),
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "_This is an automated error notification._",
                        }
                    ],
                },
            ]
        }
    else:
        items = response.get("items", [])
        subscriber_count = items[0].get("statistics", {}).get("subscriberCount", 0)
        total_channel_views = items[0].get("statistics", {}).get("viewCount", 0)
        total_videos_posted = items[0].get("statistics", {}).get("videoCount", 0)
        attachment = {
            "icon_url": IMAGE_URL,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 YouTube Channel Performance",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Untold Traces*"},
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"👥 *Subscribers*\n{subscriber_count}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"🎬 *Published Videos*\n{total_videos_posted}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"👀 *Total Channel Views*\n{total_channel_views}",
                        },
                    ],
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "_Automatically generated via YouTube Data API._",
                        }
                    ],
                },
            ],
        }
    try:
        res = requests.post(url=SLACK_URL, json=attachment)
        if not res.ok:
            print(f"slack API failed due to {res.status_code} with {res.json()}")
        print("Successfully posted the message in slack")

    except Exception as e:
        print(f"Error occured while posting the message to slack due to {e}")


def main():

    response = make_requests()
    post_to_slack(response=response)


if __name__ == "__main__":
    main()
