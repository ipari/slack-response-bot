from flask import Blueprint

viewer = Blueprint('blueprint', __name__)


@viewer.route("/")
def hello():
    return "Hello World?"


@viewer.route("/main/")
def main():
    return "Main"
