from flask import Flask, request, jsonify
import json
from downloader import controller
from os import environ

mode = environ.get("DEBUG")

app = Flask(__name__)


@app.route('/api/download', methods=['PUT'])
def videolistdownloader():
    record = json.loads(request.data)
    if (record.get('stashurl') == ''):
        return jsonify({"status": "ERROR", "message": "stashurl missing"})
    elif (record.get('method') == ''):
        return jsonify({"status": "ERROR", "message": "method missing"})
    elif (record.get('urls') == ''):
        return jsonify({"status": "ERROR", "message": "urls missing"})
    else:
        # info = test(record.get('urls'))
        info = controller(record.get('urls'), record.get('stashurl'), record.get('method'))
        return jsonify(info)

app.run(debug=mode, host='0.0.0.0')