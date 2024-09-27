import praw
from moviepy.editor import *
from dataclasses import dataclass
from typing import Literal, get_args
from transformers import pipeline, Pipeline

# temporary WIP classifier stuff
USE_CLASSIFIER: bool = False
classifier: Pipeline
if USE_CLASSIFIER:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

REDDIT_CLIENT_ID: str = ""
REDDIT_CLIENT_SECRET: str = ""
REDDIT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
reddit: praw.Reddit

def update_reddit():
    global reddit
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)

update_reddit()

POST_ID: str = ""

CLASSIFICATION_LABELS = Literal['sexual', 'violent', 'criminal', 'positive', 'useful', 'funny', 'depressing']

@dataclass
class RedditTextClassification:
    """Struct for storing text classification outputs (0-1 scores)"""
    sexual: float = 0
    violent: float = 0
    criminal: float = 0
    positive: float = 0
    useful: float = 0
    funny: float = 0
    depressing: float = 0

    def get_labels(self) -> list[str]:
        return list(get_args(CLASSIFICATION_LABELS))
    
    def get_label(self, label: CLASSIFICATION_LABELS) -> float:
        return self.__dict__[label]
    
    def get_values(self) -> list[float]:
        l = list()
        for label in self.get_labels():
            l.append(self.get_label(label))
        return l

    def set_values(self, labels: list[str], values: list[float]):
        i = 0
        for label in labels:
            self.__dict__[label] = values[i]
            i += 1
    
    def get_interesting_score(self) -> float:
        values = self.get_values()
        values.sort(reverse=True)
        return (values[0] + values[1] + values[2]) / 3

@dataclass
class RedditComment:
    id: str
    url: str
    content: str

@dataclass
class RedditStory:
    id: str
    url: str
    title: str
    content: str
    comments: list[RedditComment]
    classification: RedditTextClassification | None

REDDIT_TIMEFRAMES = Literal["all", "year", "month", "week", "day", "hour"]

def get_top_reddit_story(subreddit: str, time: REDDIT_TIMEFRAMES, comment_limit: int = 5) -> RedditStory:
    subreddit: praw.reddit.Subreddit = reddit.subreddit(subreddit)
    post = next(subreddit.top(limit=1, time_filter = time))

    comments: list[RedditComment] = list()
    for comment in post.comments:
        if len(comments) >= comment_limit:
            break
        if isinstance(comment, praw.reddit.models.MoreComments):
            continue
        if comment.body == "[deleted]":
            continue
        comments.append(RedditComment((comment.permalink[-8:])[:-1], comment.permalink, comment.body))

    story = RedditStory(post, post.url, post.title, post.selftext, comments, None)
    if USE_CLASSIFIER:
        story.classification = _classify_story(story)
    
    return story

def get_specific_story(post_url: str, comment_limit: int = 5) -> RedditStory:
    post = reddit.submission(url=post_url)
    post._fetch()# bad ???
    
    comments: list[RedditComment] = list()
    for comment in post.comments:
        if len(comments) >= comment_limit:
            break
        if isinstance(comment, praw.reddit.models.MoreComments):
            continue
        if comment.body == "[deleted]":
            continue
        comments.append(RedditComment((comment.permalink[-8:])[:-1], comment.permalink, comment.body))

    story = RedditStory(post, post.url, post.title, post.selftext, comments, None)
    if USE_CLASSIFIER:
        story.classification = _classify_story(story)
    
    return story

def _classify_story(story: RedditStory) -> RedditTextClassification:
    classification = RedditTextClassification()
    input = story.title + "\n" + story.content
    for comment in story.comments:
        input += "\n" + comment.content
    output = classifier(input, classification.get_labels(), multi_label=True)
    classification.set_values(output['labels'], output['scores'])
    return classification