import os.path

from flask import Flask, request, redirect, render_template, jsonify, send_file
from flask_restful import Api, Resource
import ConvertMP4toWAV
import CovertAVItoWAV
import CovertMKVtoWAV
import AudioToSRT

# resources for flask app
app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_VIDEO'] = 'uploads/videofiles'
app.config['UPLOAD_AUDIO'] = 'uploads/audiofiles'
app.config['UPLOAD_TEXT'] = 'uploads/textfiles'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 * 2  # 2 GB maximum file size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching

_filename = ""


@app.route('/')
def upload_form():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    global _filename
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        _filename = file.filename
        file.save(f"{app.config['UPLOAD_VIDEO']}/{file.filename}")
        return redirect('/success')  # Redirect to the success page


@app.route('/success')
def upload_success():
    return render_template('upload.html')  # Render the success page


@app.route('/convert_audio', methods=['POST'])
def convert_audio():
    global _filename
    print(f"File {_filename} to be converted to audio")
    # handle conversion of video to audio files based on input format
    # different type of video files like .mp4, .avi and .mkv are supported

    # handle mp4 file
    if _filename.endswith(".mp4"):
        ConvertMP4toWAV.convert_mp4_to_wav(input_folder=app.config['UPLOAD_VIDEO'],
                                           output_folder=app.config['UPLOAD_AUDIO'],
                                           file_name=_filename)
    if _filename.endswith(".avi"):
        CovertAVItoWAV.convert_avi_to_wav(input_folder=app.config['UPLOAD_VIDEO'],
                                          output_folder=app.config['UPLOAD_AUDIO'],
                                          file_name=_filename)
    if _filename.endswith(".mkv"):
        CovertMKVtoWAV.convert_mkv_to_wav(input_folder=app.config['UPLOAD_VIDEO'],
                                          output_folder=app.config['UPLOAD_AUDIO'],
                                          file_name=_filename)

    return render_template('audioToText.html')  # Render the audio conversion page


@app.route('/get_srt_file', methods=['POST'])
def convert_text():
    global _filename
    print("Calling audio to SRT")
    print(f"Attempting to convert {_filename} to SRT file")
    AudioToSRT.main(os.path.join(app.config['UPLOAD_AUDIO'], _filename),
                    app.config['UPLOAD_TEXT'])

    return render_template('getSrtFile.html')  # Render the audio conversion page


@app.route('/download', methods=['GET'])
def download_file():
    global _filename
    file_path = os.path.join(app.config['UPLOAD_TEXT'], _filename.split(".")[0]+".srt")
    return send_file(file_path, as_attachment=True)


@app.route("/go_home", methods=['POST'])
def go_home():
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
