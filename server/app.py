from flask import Flask, jsonify, request
from flask_cors import CORS

from train_model import train_model, model_inference, model_label

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/train', methods=['POST'])
def train():
    # Get model type
    model_type = request.form.get('model_type')

    # Get data type
    data_type = request.form.get('data_type')

    # Load data
    data_file = request.files.get('data')
    data_file.save('data')

    return jsonify(train_model(model_type, data_type))

@app.route('/inference', methods=['POST'])
def inference():
    # Get model type
    model_type = request.form.get('model_type')

    # Get data type
    data_type = request.form.get('data_type')

    # Load data
    model_file = request.files.get('model')
    model_file.save('model')

    # Load data
    data_file = request.files.get('data')
    data_file.save('data')

    return jsonify(model_inference(model_type, data_type))

@app.route('/labeling', methods=['POST'])
def labeling():
    # Get model type
    model_type = request.form.get('model_type')

    # Get data type
    data_type = request.form.get('data_type')

    # Load data
    model_file = request.files.get('model')
    model_file.save('model')

    # Load data
    related_data_file = request.files.get('related_data')
    related_data_file.save('related_data')
    unrelated_data_file = request.files.get('unrelated_data')
    unrelated_data_file.save('unrelated_data')

    return jsonify(model_label(model_type, data_type))

if __name__ == '__main__':
    app.run(port=8000)
