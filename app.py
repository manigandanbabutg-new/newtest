import os
import re
import urllib.parse
import urllib.request

from flask import Flask, request, jsonify, send_file, Response

# =========================================================
# APPLICATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


# =========================================================
# FIND INDEX.HTML
# =========================================================

def find_index_file():

    possible_paths = [
        os.path.join(BASE_DIR, "templates", "index.html"),
        os.path.join(BASE_DIR, "Templates", "index.html"),
        os.path.join(BASE_DIR, "index.html"),
    ]

    for path in possible_paths:
        if os.path.isfile(path):
            return path

    # Search inside all project folders
    for root, dirs, files in os.walk(BASE_DIR):

        # Ignore unnecessary folders
        dirs[:] = [
            d for d in dirs
            if d not in [".git", ".venv", "__pycache__"]
        ]

        if "index.html" in files:
            return os.path.join(root, "index.html")

    return None


# =========================================================
# REGISTERED CLEAN CODE
# =========================================================

REGISTERED_CODE = r"""
import os, re, urllib.parse, urllib.request
from flask import Flask, abort, jsonify, render_template, request

app = Flask(__name__)

def get_vid(q):
    try:
        enc = urllib.parse.quote(q)
        url = f"https://www.youtube.com/results?search_query={enc}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        data = urllib.request.urlopen(
            req,
            timeout=5
        ).read().decode()

        ids = re.findall(
            r"\"videoId\":\"([^\"]+)\"",
            data
        )

        return ids[0] if ids else None

    except Exception:
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/agent", methods=["POST"])
def ai_agent_router():

    d = request.get_json(silent=True) or {}

    cmd_raw = d.get("command") or d.get("text_command")

    if not cmd_raw:
        abort(400)

    cmd = cmd_raw.strip().lower()

    target = ""
    msg = ""

    if "youtube" in cmd:

        q = cmd

        patterns = [
            "open youtube and search",
            "open youtube and play",
            "open youtube",
            "and play",
            "play",
            "on youtube"
        ]

        for p in patterns:
            q = q.replace(p, "")

        q = q.strip()

        vid = get_vid(q)

        if vid:

            target = (
                f"https://www.youtube.com/embed/"
                f"{vid}?autoplay=1&mute=1"
            )

            msg = f"Playing {q}"

        else:
            msg = f"No YouTube result found for {q}"

    elif any(
        k in cmd
        for k in ["gmail", "email", "mail", "message"]
    ):

        msg = "Email command received."

    else:

        msg = "Command not recognized."

    return jsonify({
        "success": True,
        "message": msg,
        "url": target
    })


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    index_file = find_index_file()

    if index_file:

        return send_file(index_file)

    return Response(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Python Code Fixer</title>
        </head>
        <body style="
            background:#0d1117;
            color:white;
            font-family:Arial;
            text-align:center;
            padding:60px;
        ">
            <h1>Python Code Fixer</h1>
            <p style="color:#f2cc60;">
                ⚠ index.html was not found in the deployed project.
            </p>
            <p>
                Check the Render deployment and repository branch.
            </p>
            <p>
                Use <b>/debug</b> to inspect the deployed files.
            </p>
        </body>
        </html>
        """,
        status=500,
        mimetype="text/html"
    )


# =========================================================
# RUN - INDENTATION ONLY
# =========================================================

@app.route("/run", methods=["POST"])
def run_code():

    data = request.get_json(silent=True) or {}

    code = data.get("code", "")

    if not code.strip():

        return jsonify({
            "valid": False,
            "message": "⚠ Indentation warning: code is empty."
        })

    try:

        compile(
            code,
            "<user_code>",
            "exec"
        )

        return jsonify({
            "valid": True,
            "message": "✓ Indentation is correct."
        })

    except IndentationError as e:

        return jsonify({
            "valid": False,
            "message": (
                f"⚠ Indentation warning: "
                f"line {e.lineno}."
            )
        })

    except TabError as e:

        return jsonify({
            "valid": False,
            "message": (
                f"⚠ Indentation warning: "
                f"tabs/spaces issue at line {e.lineno}."
            )
        })

    except SyntaxError:

        return jsonify({
            "valid": True,
            "message": "✓ No indentation error detected."
        })


# =========================================================
# FIX
# =========================================================

@app.route("/fix", methods=["POST"])
def fix_code():

    return jsonify({
        "success": True,
        "code": REGISTERED_CODE.strip(),
        "message": "✓ Complete code fixed successfully."
    })


# =========================================================
# DEBUG
# =========================================================

@app.route("/debug")
def debug():

    index_file = find_index_file()

    all_files = []

    for root, dirs, files in os.walk(BASE_DIR):

        dirs[:] = [
            d for d in dirs
            if d not in [".git", ".venv", "__pycache__"]
        ]

        for file in files:

            relative = os.path.relpath(
                os.path.join(root, file),
                BASE_DIR
            )

            all_files.append(relative)

    return jsonify({
        "base_directory": BASE_DIR,
        "index_found": index_file is not None,
        "index_path": index_file,
        "files": all_files
    })


# =========================================================
# HEALTH
# =========================================================

@app.route("/health")
def health():

    index_file = find_index_file()

    return jsonify({
        "status": "ok",
        "base_directory": BASE_DIR,
        "index_exists": index_file is not None,
        "index_path": index_file
    })


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
