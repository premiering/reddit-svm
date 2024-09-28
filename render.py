from gtts import gTTS
from moviepy.editor import *
from moviepy.video.fx import speedx
from moviepy.video.fx.all import crop, resize
from reddit import *
import automation
from pathlib import Path

def _generate_tts(text, filename='audio.mp3', lang='en'):
    tts = gTTS(text, lang=lang)
    tts.save(filename)

def create_video(story: RedditStory, output_file: str, bg_video_path: str, bg_music_path: str, fps: int, speed: float, preview: bool):
    """Renders and saves a video using the given Reddit story and assets. Output file must be .mp4 or .avi"""
    if not output_file.endswith(".mp4") and not output_file.endswith(".avi"):
        raise Exception("Output file must be an mp4 or avi!")

    Path("temp").mkdir(parents=True, exist_ok=True)

    post_audio_file = "temp/post_audio.mp3"
    post_screenshot_file = "temp/post_screenshot.png"

    post_text = f"{story.title}\n\n{story.content}"

    clips = []

    screenshot_scale_factor = 0.9

    # create the "post" section (reading the title of the post, and the description/content)
    _generate_tts(post_text, post_audio_file)
    automation.take_post_screenshot(story.id, story.url, post_screenshot_file)
    post_audio = AudioFileClip(post_audio_file).volumex(3.0)
    post_audio_clip = ColorClip(size=(1, 1), duration=post_audio.duration, color=(0, 0, 0)).set_audio(post_audio)
    post_image_clip = ImageClip(post_screenshot_file, duration=post_audio.duration).resize(screenshot_scale_factor)
    post_clip = CompositeVideoClip([post_image_clip, post_audio_clip])
    clips.append(post_clip)

    # create all comment tts and screenshots
    for i, comment in enumerate(story.comments):
        comment_screenshot_file = f'temp/comment_screenshot_{i}.png'
        automation.take_comment_screenshot(f"https://www.reddit.com{comment.url}", comment_screenshot_file)
        comment_audio_file = f'temp/comment_audio_{i}.mp3'
        _generate_tts(comment.content, comment_audio_file)
        comment_audio = AudioFileClip(comment_audio_file).volumex(3.0)
        comment_image_clip = ImageClip(comment_screenshot_file).set_duration(comment_audio.duration).set_audio(comment_audio).resize(screenshot_scale_factor)
        clips.append(comment_image_clip)

    # finally, compose the final video
    final_video = concatenate_videoclips(clips, method="compose")

    if bg_video_path:
        bg_video = VideoFileClip(bg_video_path).subclip(0, final_video.duration)
        bg_video.fps = fps
    else:
        bg_video = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=final_video.duration)

    final_video: CompositeVideoClip = CompositeVideoClip([bg_video, final_video.set_position("center")])
    final_video.fps = fps

    if bg_music_path:
        music = AudioFileClip(bg_music_path).subclip(0, final_video.duration).volumex(0.15)
        final_audio = CompositeAudioClip([final_video.audio, music])
        final_audio.fps = 44100
        final_video = final_video.set_audio(final_audio)
    
    final_video = speedx.speedx(final_video, speed)
    if not final_video.size == (1920, 1080): # inefficent if your bg video is not 1920 1080
        print("Resizing background video to 1920x1080! This might take longer.")
        final_video = final_video.resize(1920, 1080)
    
    (w, h) = final_video.size
    final_video = crop(final_video, width=608, height=1080, x_center=w/2, y_center=h/2)
    final_video = final_video.resize((768, 1366))

    if preview:
        final_video.preview(fps=fps)

    final_video.write_videofile(output_file, threads=8)