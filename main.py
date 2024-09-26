import reddit
import render
import typer
from typing import get_args

def main(
    reddit_client_id: str = None, 
    reddit_client_secret: str = None, 
    reddit_user_agent = reddit.REDDIT_USER_AGENT,
    bg_video_path: str = None,
    bg_music_path: str = None,
    output_file: str = "output.mp4",
    subreddit: str = None, 
    top_timeframe: str = None, 
    post_url: str = None
):
    if subreddit == None and top_timeframe == None and post_url == None:
        raise Exception("Must choose to use a subreddit and top_timeframe, or a post_url!")
    
    if reddit_client_id == None or reddit_user_agent == None:
        raise Exception("Must have all Reddit API credentials to use API!")
    
    if top_timeframe not in get_args(reddit.REDDIT_TIMEFRAMES):
        raise Exception("top_timeframe must be one of the following: " + ", ".join(reddit.REDDIT_TIMEFRAMES.__args__))

    reddit.REDDIT_CLIENT_ID = reddit_client_id
    reddit.REDDIT_CLIENT_SECRET = reddit_client_secret
    reddit.REDDIT_USER_AGENT = reddit_user_agent
    reddit.update_reddit()

    story: reddit.RedditStory
    if post_url != None:
        story = reddit.get_specific_story(post_url, 3)
    else:
        story = reddit.get_top_reddit_story(subreddit, top_timeframe)
    
    print("Found story: " + story.title)
    print("Creating video to " + output_file)
    render.create_video(story, output_file, bg_video_path, bg_music_path, 60)

if __name__ == "__main__":
    typer.run(main)