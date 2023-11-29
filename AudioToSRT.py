# imports
import os
import srt
import json
import datetime
from datetime import timedelta
from google.cloud import storage
from google.cloud import speech

# server authentication
os.environ['GOOGLe_APPLICATION_CREDENTIALS'] = 'service_key.json'
storage_client = storage.Client()


# upload audio file
def upload_to_bucket(client, blob_name, path, bucket_name):
    try:
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(path)
        return f"gs://{bucket_name}/{blob_name}"
    except Exception as e:
        print(e)
        return False


# generate transcripts
def generate_transcripts(gcs_url):
    audio_client = speech.SpeechClient()
    audio_recognizer = speech.RecognitionAudio(uri=gcs_url)
    audio_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="en-US",
        enable_word_time_offsets=True,
        enable_spoken_punctuation=True,
        enable_separate_recognition_per_channel=True,
        audio_channel_count=2,
        model="video"
    )

    operation = audio_client.long_running_recognize(config=audio_config, audio=audio_recognizer)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=150)

    return response


def build_transcript(response):
    transcript_builder = []
    for result in response.results:
        for word_info in result.alternatives[0].words:
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            word = word_info.word
            transcript_builder.append((word, start_time, end_time))

    return transcript_builder


# Function to format subtitles with proper line breaks based on time
def generate_srt_subtitles(transcription_data, max_line_duration=3.0):
    current_line = []
    current_line_duration = 0.0
    subtitles = []
    subtitle_number = 1

    initial_start_time = 0.0
    for word, start_time, end_time in transcription_data:
        word_duration = end_time - start_time

        if current_line_duration + word_duration <= max_line_duration:
            current_line.append(word)
            current_line_duration += word_duration
        else:
            subtitle_text = " ".join(current_line)
            subtitles.append((subtitle_number, initial_start_time, start_time, subtitle_text))
            current_line = [word]
            initial_start_time = start_time
            current_line_duration = word_duration
            subtitle_number += 1

    if current_line:
        subtitle_text = " ".join(current_line)
        subtitles.append((subtitle_number, start_time, end_time, subtitle_text))

    return subtitles


def write_srt_file(subtitles, output_file):
    with open(output_file, 'w') as f:
        for subtitle_number, start_time, end_time, subtitle_text in subtitles:
            f.write(f"{subtitle_number}\n"
                    f"{convert_to_srt_time_format(start_time)} --> {convert_to_srt_time_format(end_time)}\n"
                    f"{subtitle_text}\n\n")


def print_srt_format(subtitles):
    for subtitle_number, start_time, end_time, subtitle_text in subtitles:
        print(f"{subtitle_number}\n"
              f"{convert_to_srt_time_format(start_time)} --> {convert_to_srt_time_format(end_time)}\n"
              f"{subtitle_text}\n")


def convert_to_srt_time_format(seconds):
    # Convert seconds to SRT time format (HH:MM:SS,mmm)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"


def main(filepath, outputdir):

    _filename = os.path.basename(filepath)
    print(f"Got file name {_filename}")
    _basename = _filename.split(".")[0]
    # main code
    file_to_cloud = _basename + ".wav"
    blob_name = _basename + ".wav"
    output_file_path = f'{_basename}.srt'
    gcs_path = upload_to_bucket(storage_client, 'audio-files/' + blob_name, file_to_cloud, 'ssdi_bucket_2023')

    if gcs_path:
        response = generate_transcripts(gcs_path)
        subtitles = generate_srt_subtitles(build_transcript(response))

        write_srt_file(subtitles, os.path.join(outputdir, output_file_path))
        print_srt_format(subtitles)
