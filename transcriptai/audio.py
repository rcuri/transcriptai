import openai
import os
from pyannote.audio import Pipeline
from pathlib import Path

def transcribe_audio_file(audio_file_path: str):
    """Transcribes the speech in audio files using OpenAI's Whisper model"""
    with open(audio_file_path, "rb") as file:
        audio_file = file.read()
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    transcript_dict = transcript.to_dict_recursive()
    return transcript_dict



def apply_speaker_diarization_to_audio_file(
        audio_file_path: str, output_directory: str, hf_access_token:str):
    """
    Applies speaker diarization to audio file and writes output to disk. 
    Requires HuggingFace access token
    """
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                    use_auth_token=hf_access_token)
    # apply the pipeline to an audio file
    diarization = pipeline(audio_file_path)

    # dump the diarization output to disk using RTTM format 
    audio_file_name = Path(audio_file_path).stem
    rttm_file_name = audio_file_name + ".rttm"
    if os.path.isdir(output_directory):
        diarization_file_path = os.path.join(
            output_directory, rttm_file_name
        )
    else:
        raise Exception("Directory does not exist")
    with open(diarization_file_path, "w") as rttm:
        diarization.write_rttm(rttm)
    return diarization_file_path