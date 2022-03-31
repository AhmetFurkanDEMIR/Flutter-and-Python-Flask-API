from flask import Flask, json, request, jsonify, send_from_directory
import os
import urllib.request
from werkzeug.utils import secure_filename

import cv2
import numpy as np
from pyzbar.pyzbar import decode
import base64

app = Flask(__name__)

app.secret_key = "demirai112s2s1dsa*"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return 'Homepage'

@app.route('/get')
def get():

    dirFiles = os.listdir(app.config['UPLOAD_FOLDER'])
    dirFiles.sort()
    file=dirFiles[len(dirFiles)-1]

    return send_from_directory(app.config["UPLOAD_FOLDER"], file, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload_file():

    if 'files' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files')
    errors = {}
    success = False

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:

        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp

    if success:

        img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        for barcode in decode(img):

            myData = barcode.data.decode('utf-8')
            pts = np.array([barcode.polygon],np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(img,[pts],True,(255,0,255),2)
            pts2 = barcode.rect
            cv2.putText(img,myData,(pts2[0],pts2[1]),cv2.FONT_HERSHEY_SIMPLEX, 0.9,(255,0,255),2)


        cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename),img)
        resp=""
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb") as img_file:
            resp = base64.b64encode(img_file.read())

        return resp

    else:

        resp = jsonify(errors)
        resp.status_code = 500

        return resp

if __name__ == '__main__':
    app.run(host="0.0.0.0" ,port=5000)
