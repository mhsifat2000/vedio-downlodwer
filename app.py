from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Create download directory
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Track download status globally
download_status = {
    'status': 'waiting',
    'filename': '',
    'error': ''
}

def download_video(url):
    global download_status
    try:
        download_status['status'] = 'downloading'
        download_status['filename'] = ''
        download_status['error'] = ''

        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        download_status['status'] = 'done'
        download_status['filename'] = os.path.basename(filename)
    except Exception as e:
        download_status['status'] = 'error'
        download_status['error'] = str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('url')
    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    # Start the download
    download_video(video_url)
    return jsonify({'message': 'Download started'})

@app.route('/progress', methods=['GET'])
def progress():
    return jsonify({
        'status': download_status['status'],
        'filename': download_status['filename'],
        'error': download_status['error']
    })

if __name__ == '__main__':
    app.run(debug=True)