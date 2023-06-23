from moviepy.editor import AudioFileClip, VideoFileClip


def trim_video_file(
        video_file_path: str, shortened_video_file_path: str, 
        new_start_time: str=None, new_end_time: str=None):
    """Change start and end time of video clip"""
    video_file_clip = VideoFileClip(video_file_path)
    if new_start_time and new_end_time:
        subclip = video_file_clip.subclip(new_start_time, new_end_time)
    elif new_start_time:
        subclip = video_file_clip.subclip(new_start_time)
    elif new_end_time:
        subclip = video_file_clip.subclip(0, new_end_time)
    subclip.write_videofile(shortened_video_file_path)
    return shortened_video_file_path


def convert_mp4_to_mp3(mp4_file_path: str, mp3_file_path: str):
    """Converts mp4 file to mp3 file and saves mp3 file"""
    converted_file = AudioFileClip(mp4_file_path)        
    converted_file.write_audiofile(mp3_file_path)
    converted_file.close()
    return mp3_file_path

