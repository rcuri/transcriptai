from moviepy.editor import AudioFileClip, VideoFileClip


def trim_video_file(
        video_file_path: str, shortened_video_file_path: str, 
        video_start_time: str, video_end_time: str):
    """Change start and end time of video clip"""
    video_file_clip = VideoFileClip(video_file_path)
    subclip = video_file_clip.subclip(video_start_time, video_end_time)
    subclip.write_videofile(shortened_video_file_path)


def convert_mp4_to_mp3(mp4_file_path: str, mp3_file_path: str):
    """Converts mp4 file to mp3 file and saves mp3 file"""
    converted_file = AudioFileClip(mp4_file_path)        
    converted_file.write_audiofile(mp3_file_path)
    converted_file.close()
