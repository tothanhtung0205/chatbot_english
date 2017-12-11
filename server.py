from flask import Flask, request
from ner_model import nlu
import json

app = Flask('nlu')


@app.route('/nlu', methods=['POST'])
def process_request():
    data = request.get_data()
    x = nlu(data)
    x = json.dumps(x)
    return x

if __name__ == '__main__':
    app.run(port=12345)