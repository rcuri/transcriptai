import openai
import os
from pyannote.audio import Pipeline


def transcribe_audio_file(
        audio_file_path: str, transcript_directory: str=None, raw_transcript_file_name: str=None):
    """Transcribes the speech in audio files using OpenAI's Whisper model"""
    audio_file = open(audio_file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    transcript_dict = transcript.to_dict_recursive()
    raw_transcript_text = transcript_dict['text']
    
    if not transcript_directory:
        transcript_file_path = os.path.join(
            os.path.dirname(__file__), "..", "training", "raw_transcripts", 
            raw_transcript_file_name
        )
    elif os.path.isdir(transcript_directory):
        transcript_file_path = os.path.join(
            transcript_directory, raw_transcript_file_name
        )
    with open(transcript_file_path, "w") as f:
        f.write(raw_transcript_text)
    return transcript_dict


def apply_speaker_diarization_to_audio_file(
        audio_file_path: str, output_directory:str, output_file_name: str):
    """
    Applies speaker diarization to audio file. 
    Requires HuggingFace access token
    """
    hf_access_token = os.getenv("HUGGING_FACE_WRITE_ACCESS_TOKEN")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                    use_auth_token=hf_access_token)
    # apply the pipeline to an audio file
    diarization = pipeline(audio_file_path)

    if not output_directory:
        diarization_file_path = os.path.join(
            os.path.dirname(__file__), "..", "training", "diarization", 
            output_file_name
        )
    elif os.path.isdir(output_directory):
        diarization_file_path = os.path.join(
            output_directory, output_file_name
        )

    # dump the diarization output to disk using RTTM format
    with open(diarization_file_path, "w") as rttm:
        diarization.write_rttm(rttm)
    return diarization