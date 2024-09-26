from moviepy.editor import *
import typer

def main(file: str):
    """Trims the provided video to the length provided. Helpful for speeding up renders when using big background videos."""

    if not file.endswith(".mp4") and not file.endswith(".avi"):
        raise Exception("Output file must be an mp4 or avi!")
    
    video = VideoFileClip(file)
    video = video.cutout(0, 1)
    video.write_videofile(file[:-4] + "-trim.mp4", fps=video.fps)

if __name__ == "__main__":
    typer.run(main)