import os
import ast
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

REGISTERED_CODE = r'''PASTE YOUR CLEAN REGISTERED_CODE HERE'''

def check_indentation(code):
    try:
        ast.parse(code)
        return {"valid": True, "message": "Indentation is correct."}
    except IndentationError as e:
        return {
            "valid": False,
            "message": f"Indentation warning: line {e.lineno}."
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "message": f"Python indentation/syntax warning: line {e.lineno}."
        }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_code():
    code = request.get_json().get("code", "")
    return jsonify(check_indentation(code))

@app.route("/fix", methods=["POST"])
def fix_code():
    return jsonify({
        "success": True,
        "code": REGISTERED_CODE,
        "message": "Code fixed successfully."
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
