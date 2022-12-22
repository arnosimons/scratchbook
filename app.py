from flask import Flask, render_template, request, send_file
from flask import url_for, jsonify

import json
from pydub import AudioSegment
from werkzeug.urls import url_unquote
import io
import os

from construction import L, make_scratch, names_in_formula
from analysis import get_info
from library import get_tutorial
from globals import FORMULA_SYMBOLS

### Open Files
##############################################################################

PATH = ""

with open(f'{PATH}resources/json/COMBINED.json', 'r') as file:
    COMBINED = json.load(file)

with open(f'{PATH}resources/json/codebook.json', 'r') as file:
    codebook = json.load(file)

with open(f"{PATH}resources/audio/ahhh.wav", "rb") as file:
    SAMPLE = AudioSegment.from_file(file, format="wav")

with open(f"{PATH}resources/audio/beat75bpm.wav", "rb") as file:
    BEAT = AudioSegment.from_file(file, format="wav")

### Initialize App
##############################################################################

app = Flask(__name__)


### Render home.html
##############################################################################

@app.route("/", methods=["GET"])
def home():
    return render_template('home.html')

### Process Formula
##############################################################################
@app.route("/process_formula", methods=["GET"])
def process_formula():
    """ Checks syntax and semantics of requested formula. Redirects if ok. """
    formula = "".join(request.values.get('formula').split())
    if not formula:
        return jsonify({
            "isWorking": False,
            "isEmpty": True,
        })
    if formula in [".", "()", "[]"]:
        return jsonify({
            "isWorking": False,
            "isEmpty": False,
            "message": "This is not a working formula.",
        })
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    allowed_chars += "_0123456789" + FORMULA_SYMBOLS
    for char in formula:
        if char not in allowed_chars:
            return jsonify({
                "isWorking": False,
                "isEmpty": False,
                "message": f'You cannot use "{char}" in a formula.',
            })
    try:
        info = get_info(make_scratch(formula, codebook))
        if info["length"] > 16:
            return jsonify({
                "isWorking": False,
                "isEmpty": False,
                "message": f'Currently, your scratch cannot be longer than 20 beats.',
            })
        tutorials = []
        known_names = [] # cause set approach would destroy the order of names!
        for name in names_in_formula(formula) + info["combos"] + info["elements"]:
            if name in known_names:
                continue
            known_names.append(name)
            link = get_tutorial(name, codebook)
            if link and not link in tutorials: 
                tutorials.append(link)
        return jsonify({
            "isWorking": True,
            "isEmpty": False,
            "processedFormula":formula,
            "info":info,
            "tutorials":tutorials,
        })
    except KeyError as e:
        return jsonify({
            "isWorking": False,
            "isEmpty": False,
            "message": f'There is no scratch called "{e.args[0]}".',
        })
    except Exception as ex:
        return jsonify({
            "isWorking": False,
            "isEmpty": False,
            "message": f"This is not a working formula: {ex}",
        })

### Render Files (svg, audio, png, preview, figures)
##############################################################################

@app.route('/formulas/<encoded_formula>/scratchbook_ttm', methods=['GET', ])
def formula_to_svg(encoded_formula):
    """Returns svg for formula"""
    formula = url_unquote(encoded_formula).replace("$","/")
    try:
        fig = make_scratch(formula, codebook).TTM(size=3)
    except Exception as ex:
        return render_template('formula_error.html', 
            type=type(ex).__name__, args=ex.args)
    fig.tight_layout()
    file = io.BytesIO()
    fig.savefig(file, format="svg")
    file.seek(0)
    return send_file(file, mimetype='image/svg+xml')

@app.route('/formulas/<encoded_formula>/scratchbook_audio', methods=['GET', ])
def formula_to_audio(encoded_formula):
    """Returns audio for formula"""
    formula = url_unquote(encoded_formula).replace("$","/")
    try:
        audio = make_scratch(formula, codebook).audio(
            sample=SAMPLE, bpm=90, instrumental=BEAT,
            muting_color="w", muting_curve=L)
    except Exception as ex:
        return render_template('formula_error.html', 
            type=type(ex).__name__, args=ex.args)
    file = io.BytesIO()
    audio.export(file, format="wav")
    file.seek(0)
    return send_file(file, mimetype='audio/wav')

@app.route('/formulas/<encoded_formula>/png', methods=['GET', ])
def formula_to_png(encoded_formula):
    """Returns png for formula"""
    formula = url_unquote(encoded_formula).replace("$","/")
    try:
        fig = make_scratch(formula, codebook).TTM()
    except Exception as ex:
        return render_template('formula_error.html', 
             type=type(ex).__name__, args=ex.args)
    fig.tight_layout()
    file = io.BytesIO()
    fig.savefig(file, format="png", bbox_inches='tight')
    file.seek(0)
    return send_file(file, mimetype='image/png')

@app.route('/formulas/<encoded_formula>/preview', methods=['GET', ])
def formula_to_preview(encoded_formula):
    """Returns png for formula"""
    formula = url_unquote(encoded_formula).replace("$","/")
    if formula + ".png" in os.listdir(f'{PATH}resources/previews'):
        return send_file(f'{PATH}resources/previews/{formula}.png', 
                        mimetype='image/png')
    try:
        fig = make_scratch(formula, codebook).preview()
    except Exception as ex:
        return render_template('formula_error.html', 
            type=type(ex).__name__, args=ex.args)
    fig.tight_layout()
    file = io.BytesIO()
    fig.savefig(file, format="png")
    file.seek(0)
    return send_file(file, mimetype='image/png')

@app.route('/figures/classes')
def classes():
    return send_file(f'{PATH}resources/figures/el_classes.png', 
                        mimetype='image/png')

@app.route('/figures/rules')
def rules():
    return send_file(f'{PATH}resources/figures/decision_tree.png', 
                        mimetype='image/png')

### Render Library (datatable)
##############################################################################

@app.route("/library/data", methods=['GET',])
def data():
    """ Prepares and sends currently visible data for library datatable """
    columns = {0:"Preview", 1:"Name(s)", 2:"sounds", 3:"F", 4:"variations", 
        5:"Formula"}
    draw = int(request.values.get('draw'))
    length = int(request.values.get('length'))
    start = int(request.values.get('start'))
    search = str(request.values.get('search[value]'))
    column = int(request.values['order[0][column]']) # implement joint sort and make order_columns a list
    sort = str(request.values['order[0][dir]']) # implement joint sort and make order_dirs a list
    libraries = str(request.values.get('columns[6][search][value]'))  
    records_total = COMBINED
    records_filtered = [ # handles search inputs
        row for row in records_total
        if any(
            lib in row["libraries"]
            for lib in libraries.split()
        )
    ]
    if search: # handles search inputs
        records_filtered = [
            row for row in records_filtered 
            if all(
                token in " ".join([str(i) for i in row.values()])
                for token in search.split()
            )
            ]
    if sort: # handles column sorting
        records_filtered = sorted(
            records_filtered, 
            key=lambda d: d[columns[column]], 
            reverse=True if sort == "desc" else False,
        ) 
    data = records_filtered[int(start):int(start + length)]
    return jsonify({
        "draw": draw,
        "recordsTotal": len(records_total),
        "recordsFiltered":len(records_filtered),
        "data":data,
    })

### Run App
##############################################################################

if __name__ == '__main__':
    app.run(debug=True)
