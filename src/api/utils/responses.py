from flask import make_response, jsonify

INVALID_FIELD_NAME_SENT_422 = {
    "http_code": 422,
    "code": "invalidField",
    "message": "Invalid Field"
}

INVALID_INPUT_422 = {
    "http_code": 422,
    "code": "invalidInput",
    "message": "Invalid Input"
}

MISSING_PARAMETERS_422 = {
    "http_code": 422,
    "code": "missingParameters",
    "message": "Missing paremters"
}

BAD_REQUEST_400 = {
    "http_code": 400,
    "code": "badRequest",
    "message": "Bad Request"
}

SERVER_ERROR_500 = {
    "http_code": 500,
    "code": "serverError",
    "message": "Server error"
}

SERVER_ERROR_404 = {
    "http_code": 404,
    "code": "notFound",
    "message": "Ressource not Found"
}


UNAUTHORIZED_403 = {
    "http_code": 403,
    "code": "notAuthorized",
    "message": "You don't have the authorization for this action"
}

SUCCESS_200 = {
    "http_code": 200,
    "code": "success"
}

SUCCESS_201 = {
    "http_code": 201,
    "code": "succes"
}

SUCCESS_204 = {
    "http_code": 204,
    "code": "succes"
}


def response_with(response, value=None, message=None, error=None,
                  headers={}, pagination=None):
    result = {}

    if response.get('message', None):
        result.update({'message': response['message']})

    if value:
        result.update(value)

    result.update({'code': response['code']})

    if error:
        result.update({'errors': error})

    if pagination:
        result.update({'pagination': pagination})

    headers.update({'Acess-Control-Allow-Origin': '*'})
    headers.update({'server': 'DBNB REST API'})

    return make_response(jsonify(result), response['http_code'], headers)
