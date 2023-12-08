import sqlite3
from flask import Flask, render_template, url_for, request, redirect, send_file, request, after_this_request
from pytube import YouTube
from pydub import AudioSegment
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'mp3', 'wav'}


def sanitize_filename(filename):
    # Replace characters that are not allowed in Windows filenames
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_db_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'db', 'database.db'))
    conn.row_factory = sqlite3.Row
    return conn


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
    video_filename = sanitize_filename(video_stream.title) + '.mp4'
    # Download the video
    video_stream.download(filename=video_filename, output_path=video_path)

    # Extract the actual filename from the downloaded video

    # Convert the video to the selected format
    selected_format = request.form.get('format', 'wav')
    if selected_format == 'mp3':
        audio = AudioSegment.from_file(video_path + video_filename, format="mp4")
        audio.export(video_path + sanitize_filename(video_stream.title) + '.mp3', format="mp3")
        return redirect(url_for('serve_audio', filename=sanitize_filename(video_stream.title) + '.mp3'))
    elif selected_format == 'wav':
        audio = AudioSegment.from_file(video_path + video_filename, format="mp4")
        audio.export(video_path + sanitize_filename(video_stream.title) + '.wav', format="wav")
        return redirect(url_for('serve_audio', filename=sanitize_filename(video_stream.title) + '.wav'))
    else:
        return "Invalid format"


@app.route('/serve_audio/<filename>')
def serve_audio(filename):
    audio_path = os.path.join(os.path.dirname(__file__), 'static/')
    ip_address = request.environ['REMOTE_ADDR']

    if request.environ.get('HTTP_X_FORWARDED_FOR') is not None:
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a proxy

    conn = get_db_connection()
    conn.execute("INSERT INTO user (ip_address, filename) VALUES (?, ?)", (ip_address, filename))
    conn.commit()  # Commit the changes to the database
    conn.close()

    file_path = os.path.join(audio_path, filename)

    @after_this_request
    def delete_files(response):
        # Delete the files after the response has been sent
        os.remove(file_path)
        os.remove(file_path[:-4] + ".mp4")
        return response

    # Send the file as an attachment
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run()
