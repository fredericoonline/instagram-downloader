import os
import uuid
import shutil
import tempfile

from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)


@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "message": "Instagram Downloader API"
    })


@app.get("/download")
def download():

    url = request.args.get("url", "").strip()

    if not url:
        return jsonify({
            "error": "URL não informada"
        }), 400

    if "instagram.com" not in url:
        return jsonify({
            "error": "URL inválida"
        }), 400

    temp_dir = tempfile.mkdtemp()

    file_id = str(uuid.uuid4())

    output_template = os.path.join(
        temp_dir,
        file_id + ".%(ext)s"
    )

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,

        "http_headers": {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/131 Safari/537.36"
        }
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

        files = os.listdir(temp_dir)

        if not files:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

            return jsonify({
                "error": "Vídeo não encontrado"
            }), 404

        video_path = os.path.join(
            temp_dir,
            files[0]
        )

        for file in files:

            if file.endswith(".mp4"):

                video_path = os.path.join(
                    temp_dir,
                    file
                )

                break

        @after_this_request
        def cleanup(response):

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

            return response

        return send_file(
            video_path,
            as_attachment=True,
            download_name="instagram-video.mp4"
        )

    except Exception as e:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        print("ERRO:", str(e))

        return jsonify({
            "error": "Não foi possível baixar o vídeo",
            "details": str(e)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
