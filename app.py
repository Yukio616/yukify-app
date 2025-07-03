from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yukify.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

class MediaFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filetype = db.Column(db.String(20), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            db.session.add(MediaFile(filename=filename, filetype=ext))
            db.session.commit()
            return redirect(url_for('index'))

    files = MediaFile.query.order_by(MediaFile.upload_time.desc()).all()
    return render_template('index.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000)
