import os
import tempfile
import json
import secrets
import yaml
import docker
from settings import MODELS_PATH, MODEL_META_FILENAME, DATA_TMP_PATH

client = docker.from_env()


def list_available_models():
    paths = os.listdir(MODELS_PATH)
    folders = []
    for path in paths:
        full_path = os.path.join(MODELS_PATH, path)
        if os.path.isdir(full_path) and path[0] != '.' and is_model_dir_valid(full_path):
            folders.append(path)

    return folders


def is_model_dir_valid(full_path):
    paths = os.listdir(full_path)
    return MODEL_META_FILENAME in paths


def get_model(model_name):
    try:
        model_path = os.path.abspath(os.path.join(MODELS_PATH, model_name))
        meta_file_path = os.path.join(model_path, MODEL_META_FILENAME)
        with open(meta_file_path, 'r') as f:
            meta = yaml.load(f.read())
            return {
                'name': model_name,
                'path': model_path,
                'meta': meta
            }
    except FileNotFoundError:
        return None


def build_model_image(model):
    image_name = get_image_name(model)
    dir_path = model.get('path')
    dockerfile = model['meta'].get('dockerfile')
    return client.images.build(path=dir_path, dockerfile=dockerfile, tag=image_name)


def get_model_image(model):
    image_name = get_image_name(model)
    try:
        return client.images.get(image_name)
    except docker.errors.ImageNotFound:
        return None


def get_image_name(model):
    image_name = model['meta'].get('image_name')
    if not image_name:
        image_name = model['meta'].get('image_name')
    if not image_name:
        image_name = model.get('name')
    return image_name


def run_model(model, args):
    with tempfile.TemporaryDirectory(dir=os.path.abspath(DATA_TMP_PATH)) as tmp_dir:
        input_file_path = os.path.join(tmp_dir, 'data.in')
        output_file_path = os.path.join(tmp_dir, 'data.out')

        with open(input_file_path, 'w') as f:
            f.write(json.dumps(args))

        with open(output_file_path, 'w') as f:
            f.write('')

        volumes = {
            input_file_path: {'bind': '/data.in'},
            output_file_path: {'bind': '/data.out'}
        }
        image_name = get_image_name(model)
        environment = {
            'X_INPUT_DATA_FILE': '/data.in',
            'X_OUTPUT_DATA_FILE': '/data.out'
        }

        container = client.containers.run(image=image_name, volumes=volumes, environment=environment, detach=False, remove=True)
        
        with open(output_file_path, 'r') as f:
            raw_output = f.read()
            try:
                output = json.loads(raw_output)
            except:
                output = raw_output
            return output, container
