from io import BytesIO
import os
import tempfile
from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename

from reformat import convert

app = Flask(__name__)

HTML = """
<!doctype html>
<title>HEIC to PNG Converter</title>
<style>
body{font-family:sans-serif;margin:2em;}
.dropzone{border:2px dashed #ccc;padding:2em;text-align:center;cursor:pointer;}
</style>
<h1>HEIC to PNG Converter</h1>
<div class="dropzone" id="dropzone">Drag & drop HEIC files here or click to select.</div>
<form id="form" method="POST" enctype="multipart/form-data" style="display:none;">
<input id="file" type="file" name="files" multiple accept=".heic,.heif"/>
</form>
<script>
const dz=document.getElementById('dropzone');
const fileInput=document.getElementById('file');
dz.addEventListener('click',()=>fileInput.click());
dz.addEventListener('dragover',e=>{e.preventDefault();});
dz.addEventListener('drop',e=>{e.preventDefault();fileInput.files=e.dataTransfer.files;document.getElementById('form').submit();});
</script>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    if not files:
        return 'No files uploaded', 400
    if len(files) == 1:
        f = files[0]
        filename = secure_filename(f.filename)
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1]) as src, \
             tempfile.NamedTemporaryFile(suffix='.png') as dst:
            f.save(src.name)
            convert(src.name, dst.name, overwrite=True)
            dst.seek(0)
            return send_file(BytesIO(dst.read()), as_attachment=True,
                             download_name=os.path.splitext(filename)[0] + '.png',
                             mimetype='image/png')
    else:
        import zipfile
        with tempfile.TemporaryDirectory() as tmpdir:
            archive = os.path.join(tmpdir, 'converted.zip')
            with zipfile.ZipFile(archive, 'w') as zf:
                for f in files:
                    filename = secure_filename(f.filename)
                    src_path = os.path.join(tmpdir, filename)
                    dst_filename = os.path.splitext(filename)[0] + '.png'
                    dst_path = os.path.join(tmpdir, dst_filename)
                    f.save(src_path)
                    convert(src_path, dst_path, overwrite=True)
                    zf.write(dst_path, dst_filename)
            return send_file(archive, as_attachment=True, mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)
