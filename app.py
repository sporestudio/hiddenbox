from flask import Flask, request, jsonify, send_from_directory, render_template
import sqlite3
import os

app = Flask(__name__, static_folder="static")
UPLOAD_FOLDER = './uploads'
DATABASE = './db/files.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('./db', exist_ok=True)


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            path TEXT NOT NULL
        )
    ''')
    conn.commit
    conn.close


# main page
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# Upload files route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Registrar en la base de datos
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO files (filename, path) VALUES (?, ?)', (file.filename, file_path))
    conn.commit()
    conn.close()

    return jsonify({"message": "File uploaded successfully"}), 201


## Route to download the files
@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT filename, path FROM files WHERE id = ?', (file_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return jsonify({"error": "File not found"}), 404
    
    filename, path = result
    directory = os.path.dirname(path)
    return send_from_directory(directory, filename, as_attachment=True)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)