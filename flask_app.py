from flask import Flask, render_template, url_for, request, redirect, send_file
from pytube import YouTube
from pydub import AudioSegment
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'mp3', 'wav'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return render_template('main_page.html')


@app.route('/api/v1/ytlink', methods=["POST"])
def download():
    yt_url = request.form['youtubeUrl']
    yt = YouTube(yt_url)
    video_stream = yt.streams.get_highest_resolution()
    video_path = os.path.join(os.path.dirname(__file__), 'static/')
    print("video path: " + video_path)
    video_filename = video_stream.title + '.mp4'
    # Download the video
    video_stream.download(filename=video_filename, output_path =video_path)

    # Extract the actual filename from the downloaded video

    print("title: " + video_stream.title)
    # Convert the video to the selected format
    selected_format = request.form.get('format', 'wav')
    if selected_format == 'mp3':
        audio = AudioSegment.from_file(video_path + video_filename, format="mp4")
        audio.export(video_path + video_stream.title + '.mp3', format="mp3")
        return redirect(url_for('serve_audio', filename=video_stream.title + '.mp3'))
    elif selected_format == 'wav':
        audio = AudioSegment.from_file(video_path + video_filename, format="mp4")
        audio.export(video_path + video_stream.title + '.wav', format="wav")
        return redirect(url_for('serve_audio', filename=video_stream.title + '.wav'))
    else:
        return "Invalid format"


@app.route('/serve_audio/<filename>')
def serve_audio(filename):
    audio_path = os.path.join(os.path.dirname(__file__), 'static/')
    print("serve audio: " + audio_path)
    return send_file(audio_path + filename, as_attachment=True)


if __name__ == '__main__':
    app.run()