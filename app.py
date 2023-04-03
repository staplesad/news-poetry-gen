import random
from urllib.parse import quote

from flask import Flask, redirect, render_template, request
from flask_caching import Cache

from poetry_gen.poem_generator import PoemGenerator
from poetry_gen.pygooglerss import search_loop

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "FileSystemCache",  # Flask-Caching related configs
    "CACHE_DIR": "cache",
}
app = Flask(__name__)

app.config.from_mapping(config)
cache = Cache(app)

pg = PoemGenerator([])


@app.route("/oops")
def show_error(err_type, status):
    return f"{err_type} had an issue. Response was {status}. please try again later"


@app.route("/poem")
def gen_poem():
    lines = pg.get_poem()
    return render_template("poem.html", lines=lines)


@app.route("/get_headlines", methods=["POST"])
def get_headlines():
    # add some error handling here
    headlines = search_loop(request.form["search-query"])
    cache.set("current_headlines", headlines)
    pg.lines = headlines
    pg.analyse_lines()
    return redirect("/poem")


@app.route("/", defaults={"query_string": None})
@app.route("/<query_string>")
def search_form(query_string):
    if query_string:
        query_string = quote(query_string)
    print(query_string)
    return render_template("index.html", query=query_string)
