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
<input id="file" type="file" multiple accept=".heic,.heif" style="display:none" />
<script>
const dz=document.getElementById('dropzone');
const fileInput=document.getElementById('file');

function upload(files){
  const formData=new FormData();
  for(const f of files){formData.append('files',f);} 
  fetch('/',{method:'POST',body:formData})
    .then(res=>res.blob().then(b=>[res,b]))
    .then(([res,blob])=>{
      const dispo=res.headers.get('Content-Disposition')||'';
      const match=/filename="?([^";]+)"?/i.exec(dispo);
      const name=match?match[1]:'download';
      const url=URL.createObjectURL(blob);
      const a=document.createElement('a');
      a.href=url;a.download=name;document.body.appendChild(a);a.click();
      setTimeout(()=>{URL.revokeObjectURL(url);a.remove();},100);
    });
}

dz.addEventListener('click',()=>fileInput.click());
fileInput.addEventListener('change',()=>{if(fileInput.files.length)upload(fileInput.files);});
dz.addEventListener('dragover',e=>{e.preventDefault();});
dz.addEventListener('drop',e=>{e.preventDefault();upload(e.dataTransfer.files);});
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
            return send_file(
                archive,
                as_attachment=True,
                download_name='converted.zip',
                mimetype='application/zip',
            )

if __name__ == '__main__':
    app.run(debug=True)
