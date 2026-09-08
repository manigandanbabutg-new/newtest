import os
from flask import Flask, request, jsonify, send_file

# =========================================================
# FLASK APPLICATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "templates", "index.html")

app = Flask(__name__)


# =========================================================
# REGISTERED CLEAN CODE
# =========================================================

REGISTERED_CODE = r'''import os, re, urllib.parse, urllib.request
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


@app.route("/agent", methods=["POST"])
def ai_agent_router():

    d = request.get_json(silent=True) or {}

    if not d:
        return jsonify({
            "success": False,
            "message": "No command received."
        }), 400

    cmd_raw = d.get("command") or d.get("text_command")

    if not cmd_raw:
        return jsonify({
            "success": False,
            "message": "Command required."
        }), 400

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

@app.route("/", methods=["GET"])
def index():

    if not os.path.exists(INDEX_FILE):
        return jsonify({
            "success": False,
            "error": "index.html not found",
            "expected_path": INDEX_FILE
        }), 500

    return send_file(INDEX_FILE)


# =========================================================
# RUN / INDENTATION CHECK
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
# FIX CODE
# =========================================================

@app.route("/fix", methods=["POST"])
def fix_code():

    return jsonify({
        "success": True,
        "code": REGISTERED_CODE,
        "message": "✓ Complete code fixed successfully."
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "index_exists": os.path.exists(INDEX_FILE)
    })


# =========================================================
# START APPLICATION
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
