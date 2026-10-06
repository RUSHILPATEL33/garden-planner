from datetime import date
from urllib.error import URLError
from urllib.request import Request, urlopen
import json

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT_SECONDS = 120


def india_season(today=None):
    """Map a date to a simple Indian gardening season."""
    month = (today or date.today()).month
    if month in (6, 7, 8, 9):
        return "monsoon"
    if month in (3, 4, 5):
        return "summer"
    return "winter"


def ask_ollama(city, season):
    prompt = (
        f"You are a practical kitchen-garden advisor for India.\n"
        f"City: {city}\n"
        f"Current season: {season}\n"
        f"Today: {date.today().isoformat()}\n\n"
        "Recommend what a home gardener should plant this week. "
        "Keep the answer short (about 120-180 words). Include:\n"
        "1) 4-6 crops that fit this season and a typical Indian climate for that city\n"
        "2) One planting tip for this week\n"
        "3) One caution (heat, rain, frost, pests) if relevant\n"
        "Write in plain language. Do not mention that you are an AI."
    )
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.4, "num_predict": 350},
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = (data.get("response") or "").strip()
    if not text:
        raise RuntimeError("Ollama returned an empty response.")
    return text


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/plant")
def plant():
    payload = request.get_json(silent=True) or {}
    city = (payload.get("city") or request.form.get("city") or "").strip()
    if not city:
        return jsonify({"error": "Please enter a city."}), 400

    season = india_season()
    try:
        advice = ask_ollama(city, season)
    except URLError:
        return (
            jsonify(
                {
                    "error": (
                        "Could not reach Ollama at http://localhost:11434. "
                        "Start Ollama and pull gemma3:4b, then try again."
                    )
                }
            ),
            503,
        )
    except TimeoutError:
        return (
            jsonify(
                {
                    "error": (
                        "Ollama took too long to answer. The model may still be loading. "
                        "Wait a moment and try again."
                    )
                }
            ),
            504,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify({"city": city, "season": season, "advice": advice})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
