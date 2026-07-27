import os
import io
import zipfile
import argparse
import tempfile
import mimetypes
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from natsort import natsorted

app = Flask(__name__)

# Formats d'images supportés
SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')

def is_image(filename):
    return filename.lower().endswith(SUPPORTED_EXTENSIONS)

def get_mime_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    custom_mimes = {
        '.webp': 'image/webp',
        '.avif': 'image/avif',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg'
    }
    return custom_mimes.get(ext) or mimetypes.guess_type(filename)[0] or 'application/octet-stream'

@app.route('/')
def index():
    base = app.config.get('BASE_TARGET')
    
    # Si aucun argument n'a été passé au lancement
    if not base:
        return render_template('index.html', files=None, base_dir="En attente d'archive (Drag & Drop)")
        
    # Si l'argument CLI est un fichier
    if os.path.isfile(base) and base.lower().endswith('.cbz'):
        return redirect(url_for('read_cbz', file=base))
        
    # Si l'argument CLI est un dossier
    elif os.path.isdir(base):
        files = [f for f in os.listdir(base) if f.lower().endswith('.cbz')]
        files = natsorted(files) # Tri naturel alphanumérique
        file_data = [{'name': f, 'path': os.path.join(base, f)} for f in files]
        return render_template('index.html', files=file_data, base_dir=base)
    
    return "Chemin invalide ou non supporté.", 400

@app.route('/read')
def read_cbz():
    file_path = request.args.get('file')
    
    if not file_path or not os.path.exists(file_path):
        return "Fichier introuvable.", 404

    try:
        with zipfile.ZipFile(file_path, 'r') as archive:
            images = [f for f in archive.namelist() if is_image(f)]
            images = natsorted(images)
    except zipfile.BadZipFile:
        return "Erreur : Fichier CBZ corrompu ou invalide.", 400

    parent_dir = os.path.dirname(file_path)
    try:
        cbz_files = natsorted([f for f in os.listdir(parent_dir) if f.lower().endswith('.cbz')])
        current_filename = os.path.basename(file_path)
        current_idx = cbz_files.index(current_filename)
        
        prev_file = os.path.join(parent_dir, cbz_files[current_idx - 1]) if current_idx > 0 else None
        next_file = os.path.join(parent_dir, cbz_files[current_idx + 1]) if current_idx < len(cbz_files) - 1 else None
    except (ValueError, FileNotFoundError):
        prev_file = next_file = None

    return render_template('reader.html', 
                           filename=os.path.basename(file_path),
                           file_path=file_path,
                           images=images,
                           prev_file=prev_file,
                           next_file=next_file)

@app.route('/image')
def get_image():
    file_path = request.args.get('file')
    image_name = request.args.get('img')

    if not file_path or not image_name:
        return "Paramètres manquants", 400

    try:
        with zipfile.ZipFile(file_path, 'r') as archive:
            img_data = archive.read(image_name)
        
        mime_type = get_mime_type(image_name)
        return send_file(io.BytesIO(img_data), mimetype=mime_type)
    except Exception as e:
        return f"Erreur de lecture d'image: {str(e)}", 500

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.cbz'):
        return jsonify({'error': 'Fichier invalide, un .cbz est requis.'}), 400

    temp_dir = tempfile.gettempdir()
    safe_name = secure_filename(file.filename)
    save_path = os.path.join(temp_dir, safe_name)
    file.save(save_path)

    return jsonify({'url': url_for('read_cbz', file=save_path)})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Lecteur d'archives CBZ Web Local")
    parser.add_argument('path', type=str, nargs='?', default=None, help="Chemin vers un fichier .cbz ou un dossier contenant des .cbz (optionnel)")
    args = parser.parse_args()

    if args.path:
        abs_path = os.path.abspath(args.path)
        if not os.path.exists(abs_path):
            print(f"Erreur : Le chemin '{abs_path}' n'existe pas.")
            exit(1)
        app.config['BASE_TARGET'] = abs_path
        print(f"[*] Cible : {abs_path}")
    else:
        app.config['BASE_TARGET'] = None
        print(f"[*] Démarrage à vide. Prêt pour le Drag & Drop.")
    
    print(f"[*] Démarrage du serveur...")
    
    Timer(1, lambda: webbrowser.open_new("http://127.0.0.1:5000")).start()
    
    app.run(host='127.0.0.1', port=5000, debug=False)