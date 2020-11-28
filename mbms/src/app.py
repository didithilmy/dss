from flask import request
from flask_api import FlaskAPI, status
import settings
from docker.errors import ImageNotFound, ContainerError
from models import list_available_models, get_model, build_model_image, get_model_image, run_model as execute_model

app = FlaskAPI(__name__)


@app.route('/models/', methods=['GET'])
def models():
    models = list_available_models()
    return {'models': models}


@app.route('/models/<model_name>/', methods=['GET'])
def describe_model(model_name):
    model = get_model(model_name)
    if model:
        return model
    else:
        return {'error': "Model not found or incorrectly configured"}, status.HTTP_404_NOT_FOUND


@app.route('/models/<model_name>/build/', methods=['GET', 'POST'])
def build_model(model_name):
    if request.method == 'GET':
        return {'error': "Method not allowed"}, status.HTTP_405_METHOD_NOT_ALLOWED

    model = get_model(model_name)
    if not model:
        return {'error': "Model not found or incorrectly configured"}, status.HTTP_404_NOT_FOUND

    image, logs = build_model_image(model)
    return {'success': True, 'image': image.attrs}


@app.route('/models/<model_name>/image/', methods=['GET'])
def describe_image(model_name):
    model = get_model(model_name)
    if not model:
        return {'error': "Model not found or incorrectly configured"}, status.HTTP_404_NOT_FOUND

    image = get_model_image(model)
    if not image:
        return {'error': "Image has not been built"}, status.HTTP_404_NOT_FOUND

    return image.attrs


@app.route('/models/<model_name>/run/', methods=['GET', 'POST'])
def run_model(model_name):
    if request.method == 'GET':
        return {'error': "Method not allowed"}, status.HTTP_405_METHOD_NOT_ALLOWED

    model = get_model(model_name)
    if not model:
        return {'error': "Model not found or incorrectly configured"}, status.HTTP_404_NOT_FOUND

    try:
        output, logs = execute_model(model, request.data)
        return {'output': output, 'logs': logs.decode("utf-8").split('\n')}
    except ContainerError:
        return {'error': "Container error"}, status.HTTP_500_INTERNAL_SERVER_ERROR
    except ImageNotFound:
        return {'error': "Image has not been built"}, status.HTTP_404_NOT_FOUND
