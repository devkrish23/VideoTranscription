import os
from moviepy.editor import AudioFileClip

def convert_mkv_to_wav(input_folder, output_folder, file_name):
    input_file_path = os.path.join(input_folder, file_name)
    output_file_name = os.path.splitext(file_name)[0] + ".wav"
    output_file_path = os.path.join(output_folder, output_file_name)
    print("Converting MKV to wav format")

    if not os.path.exists(input_file_path):
        print("Error: The input file does not exist.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        audio_clip = AudioFileClip(input_file_path)
        audio_clip.write_audiofile(output_file_path, codec='pcm_s16le')
        print(f"Success: The WAV file has been saved to {output_file_path}")
    except Exception as e:
        print("Error: An error occurred during the conversion process.")
        print("Error details:", str(e))
    finally:
        if 'audio_clip' in locals():
            audio_clip.close()

if __name__ == "__main__":
    input_folder = input("Enter the path of the folder containing the MKV file: ")
    output_folder = input("Enter the path of the folder to save the WAV file: ")
    file_name = input("Enter the name of the MKV file (including the extension): ")
    convert_mkv_to_wav(input_folder, output_folder, file_name)
