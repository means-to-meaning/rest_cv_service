import base64
import copy
import os
import random
import time
import datetime
from flask import Flask, abort, request, jsonify
from threading import Lock
import predict
from PIL import Image
from io import BytesIO

script_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # limit uploads to 16MBytes

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
lock = Lock()
last_object_class = ""
last_object_count = 0
last_object_ts = time.time()
last_object_target_count = 3
detected_object_class = ""

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def process_img(img):
    # time.sleep(2)
    preds = predict.predict_class(img)
    with lock:
        global last_object_class
        global last_object_count
        global last_object_ts
        global detected_object_class
        last_object_ts = time.time()
        detected_object_class = ""
        if last_object_class == preds and (last_object_ts - time.time()) < 1:
            last_object_count += 1
            if last_object_count == last_object_target_count:
                detected_object_class = last_object_class
                last_object_count = 0
                print(detected_object_class)
        else:
            last_object_class = copy.deepcopy(preds)
            last_object_count = 0


    return True

@app.route('/', methods=['GET'])
def help():
    return jsonify({'supported_requests': [{'POST': '/upload'}, {'GET': '/most_recent_object'}]})

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
        elif 'file' in request.files:
            file = request.files['file']
        else:
            abort(404)
        if file and allowed_file(file.filename):
            image_string = base64.b64encode(file.read())
            decoded = base64.b64decode(image_string)
            img = Image.open(BytesIO(decoded))
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')
            file.save(os.path.join(script_dir, "storage", st + ".jpg"))
            res = process_img(img)
            if res:
                # return jsonify(res)
                return 'OK'
            else:
                abort(404)

@app.route('/most_recent_object', methods=['GET'])
def get_most_recent_object():
    if request.method == 'GET':
        with lock:
            global detected_object_class
            ans = copy.deepcopy(detected_object_class)
        return jsonify(ans)
    else:
        abort(404)

if __name__ == '__main__':
    app.run()


