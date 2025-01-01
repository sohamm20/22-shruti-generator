# import librosa
# import soundfile as sf
# import numpy as np
#
# octaveMap = {-1: "low", 0: "mid", 1: "high"}
# fileFormat = ".wav"
#
# cents = [
#     90,
#     112,
#     182,
#     204,
#     294,
#     316,
#     386,
#     408,
#     498,
#     519,
#     590,
#     612,
#     792,
#     813,
#     884,
#     906,
#     996,
#     1017,
#     1088,
#     1110,
# ]
#
# for octave in range(-1, 2, 1):
#
#     def shift_pitch(audio_path, output_path, cents):
#         y, sr = librosa.load(audio_path, sr=None)
#
#         factor = 2 ** (cents / 1200.0)
#
#         y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=np.log2(factor) * 12)
#
#         sf.write(output_path, y_shifted, sr)
#         print(f"Audio saved to {output_path}")
#
#     input_audio = f"C{fileFormat}"
#
#     Swar = ["Re", "Ga", "Ma", "Dha", "Ni"]
#     Variant = ["komal", "teevra"]
#     Shruti = ["low", "high"]
#
#     for i in range(0, 20):
#         curr = Swar[i // 4] + f"_{octaveMap[octave]}_" + Variant[(i % 4) // 2] + "_" + Shruti[i % 2] + fileFormat
#         shift_pitch(input_audio, curr, cents[i] + octave * 1200)
#     shift_pitch(input_audio, f"Sa_{octaveMap[octave]}_komal_low" + fileFormat, octave * 1200)
#     shift_pitch(input_audio, f"Pa_{octaveMap[octave]}_komal_low" + fileFormat, 702 + octave * 1200)

from flask import Flask, request, send_file, render_template_string
import librosa
import soundfile as sf
import numpy as np
import os
import shutil
import zipfile
import uuid

app = Flask(__name__)

octaveMap = {-1: "low", 0: "mid", 1: "high"}
fileFormat = ".mp3"
cents = [90,112,182,204,294,316,386,408,498,519,590,612,792,813,884,906,996,1017,1088,1110]

def shift_pitch(audio_path, output_path, cents):
    y, sr = librosa.load(audio_path, sr=None)
    factor = 2 ** (cents / 1200.0)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=np.log2(factor)*12)
    sf.write(output_path, y_shifted, sr)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audio' not in request.files or request.files['audio'].filename == '':
            return "No selected file"

        unique_id = str(uuid.uuid4())
        temp_dir = f"temp_{unique_id}"
        os.makedirs(temp_dir, exist_ok=True)

        audio = request.files['audio']
        input_path = os.path.join(temp_dir, audio.filename)
        audio.save(input_path)

        for octave in range(-1, 2):
            for i in range(20):
                out_name = (f"{['Re','Ga','Ma','Dha','Ni'][i//4]}_{octaveMap[octave]}_"
                            f"{['komal','teevra'][(i%4)//2]}_{['low','high'][i%2]}{fileFormat}")
                shift_pitch(input_path, os.path.join(temp_dir, out_name), cents[i] + octave*1200)
            shift_pitch(input_path, os.path.join(temp_dir, f"Sa_{octaveMap[octave]}_komal_low{fileFormat}"), octave*1200)
            shift_pitch(input_path, os.path.join(temp_dir, f"Pa_{octaveMap[octave]}_komal_low{fileFormat}"), 702+octave*1200)

        zip_filename = f"converted_{unique_id}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)

        shutil.rmtree(temp_dir)
        return send_file(zip_filename, as_attachment=True)

    html_form = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Pitch Shift Converter</title>
      <link rel="stylesheet"
       href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
      <div class="container py-5">
        <div class="card shadow-sm mx-auto" style="max-width: 30rem;">
          <div class="card-body">
            <h4 class="card-title text-center">22 Shruti Converter</h4>
            <p class="card-text text-center text-muted mb-4">
              Upload a .mp3 file to shift pitches.
            </p>
            <form method="POST" enctype="multipart/form-data">
              <div class="mb-3">
                <input class="form-control" type="file" name="audio" accept=".mp3" required />
              </div>
              <div class="d-grid">
                <button class="btn btn-primary" type="submit" onclick="showLoading()">
                  Convert
                </button>
              </div>
            </form>
            <div id="loading" class="text-center mt-3" style="display:none;">
              <div class="spinner-border text-primary" role="status"></div>
              <p class="text-muted">Processing...</p>
            </div>
          </div>
        </div>
      </div>
      <script>
        function showLoading() {
          document.getElementById('loading').style.display = 'block';
        }
      </script>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html_form)

if __name__ == '__main__':
    app.run(debug=True)