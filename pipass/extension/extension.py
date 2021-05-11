from flask import Flask, request, jsonify
from flask_restful import Api
from time import sleep

from pipass.connection import Connection, Command

app = Flask(__name__)
api = Api(app)
port = 5193

app.config["APPLICATION_ROOT"] = "/api"

def await_for_device_response(type, *args, **kwargs):
    def decorator(func):
        def wrapper(*largs, **lkwargs):
            try:
                connection = Connection.get_instance_or_error()
            except:
                return func(response=None, *largs, **lkwargs)
            response = None

            def fill_response(response_body):
                nonlocal response 
                if response == None:
                    response = response_body.copy()

            connection.bind(on_receive=fill_response, type=type)
            connection.send_command_with_type(type=type, *args, **kwargs)
            
            while response is None:
                sleep(0.1)
                print(response)

            return func(response=response, *largs, **lkwargs)
        # Flask error
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


@app.route('/', methods=['GET'])
def root():
    return jsonify({'status': 'online'})

@app.route('/hello', methods=['GET'])
@await_for_device_response(type=Command.Types.APP_HELLO)
def hello(response):
    return jsonify({'status': response['options']})

@app.route('/send-pin', methods=['POST'])
def send_pin():
    body = request.get_json(force=True)

    response = await_for_device_response(
        type=Command.Types.ASK_FOR_PIN,
        pin=body['pin']
    )(lambda response: response)()

    return jsonify({'status': response['reply_code'].value})

@app.route('/list-credentials', methods=['GET']) 
@await_for_device_response(type=Command.Types.LIST_CREDENTIALS)
def get_credentials(response):
    return jsonify(response['options'])

@app.route('/credential-details', methods=['POST']) 
def get_credential_details():
    body = request.get_json(force=True)

    response = await_for_device_response(
        type=Command.Types.CREDENTIAL_DETAILS,
        name=body['name']
    )(lambda response: response)()

    return jsonify(response['options'])

@app.route('/encrypted-field', methods=['POST']) 
def get_encyrpted_field():
    body = request.get_json(force=True)

    response = await_for_device_response(
        type=Command.Types.ENCRYPTED_FIELD_VALUE,
        credential_name=body['credential_name'],
        field_name=body['field_name'],
    )(lambda response: response)()

    return jsonify(response['options'])

@app.route('/add-credential', methods=['PUT']) 
def add_credential():
    body = request.get_json(force=True)

    response = await_for_device_response(
        type=Command.Types.ADD_CREDENTIAL,
        form_information=body['form_information'],
    )(lambda response: response)()

    return jsonify({'status': response['reply_code'].value})


    

    


def run_server():
    app.run(host="0.0.0.0", port=port)