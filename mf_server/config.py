import secrets
import os
from flask import request, jsonify
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split()[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        if token != os.environ.get("MF_AUTH_TOKEN"):
            return jsonify({"message": "Invalid token!"}), 401

        return f(*args, **kwargs)

    return decorated


def generate_auth_token(token_len: int = 16) -> str:
    """
    Generates authorization token

    Args:
        token_len (int, optional): Authorization token length. Defaults to 16.

    Returns:
        str: Randomly generated hexadecimal authorization token
    """
    return secrets.token_hex(token_len)
