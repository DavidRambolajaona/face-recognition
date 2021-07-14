from flask import Blueprint, render_template, request, redirect, jsonify, escape
from flask.helpers import url_for
from requests.api import get
from appli.service.joke.joke import getJoke

home_bp = Blueprint('home_bp', __name__, template_folder='template', static_folder='static', static_url_path='/home-static')

@home_bp.route('/')
def index():
    joke = getJoke()
    return render_template("home.html", joke = joke)

@home_bp.route('/joke/api/get')
def joke() :
    nb = request.args.get("nb")
    if nb is not None  :
        nb = int(nb)
    else :
        nb = 1
    jokes = []
    for i in range(0, nb) :
        joke = getJoke()
        jokes.append(joke)
    return jsonify(jokes)