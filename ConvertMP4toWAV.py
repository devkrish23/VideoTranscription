import os
from moviepy.editor import AudioFileClip


def convert_mp4_to_wav(input_folder, output_folder, file_name):
    # Construct the input and output file paths
    input_file_path = os.path.join(input_folder, file_name)
    output_file_name = os.path.splitext(file_name)[0] + ".wav"
    output_file_path = os.path.join(output_folder, output_file_name)

    print("Check", input_file_path)
    print("Converting MP4 to wav format")
    # Check if the input file exists
    if not os.path.exists(input_file_path):
        print("Error: The input file does not exist.")
        return

    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Extract audio from the video file and save it as WAV
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


"""
if __name__ == "__main__":
    # Take input from the user
    input_folder = input("Enter the path of the folder containing the MP4 file: ")
    output_folder = input("Enter the path of the folder to save the WAV file: ")
    file_name = input("Enter the name of the MP4 file (including the extension): ")

    # Perform the conversion
    convert_mp4_to_wav(input_folder, output_folder, file_name)
"""