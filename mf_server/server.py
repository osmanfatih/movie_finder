import os
from pathlib import Path
from flask import Flask, request, jsonify

from mf_server.config import token_required

from mf_utils import logger_setup

# Setup logger
logger = logger_setup.get_logger()

app = Flask(__name__)


@app.route("/get_available", methods=["GET"])
@token_required
def get_available():
    pass


if __name__ == "__main__":
    app.run(debug=True, port=8899)
