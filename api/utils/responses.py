from flask import make_response, jsonify

INVALID_INPUT_422 = {
    "http_code": 422,
    "code": "invalideInput",
    "msg": "Champs Invalide"
}

BAD_REQUEST_400 = {
    "http_code": 400,
    "code": "badRequest",
    "msg": "Mauvaise Requête"
}

SERVER_ERROR_500 = {
    "http_code": 500,
    "code": "serverError",
    "msg": "Erreur Serveur"
}

SERVER_ERROR_404 = {
    "http_code": 404,
    "code": "notFound",
    "msg": "Ressource Introuvable"
}

UNAUTHORIZED_403 = {
    "http_code": 403,
    "code": "notAuthorized",
    "msg": "Vous n'avez pas l'autorisation pour cette action"
}

SUCCESS_200 = {
    "http_code": 200,
    "code": "success"
}

SUCCESS_201 = {
    "http_code": 201,
    "code": "success"
}

SUCCESS_204 = {
    "http_code": 204,
    "code": "success"
}


def response_with(response, value=None, message=None, error=None,
                  headers={}, pagination=None):
    result = {}

    if response.get('msg', None):
        result.update({'msg': response['msg']})

    if message:
        result.update({'msg': message})

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
