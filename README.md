# Garden Planner

A small local web app: you type an Indian city, and it tells you **what to plant this week**.

The page stays simple — a city box, a **What should I plant?** button, and the advice below. The season (monsoon, winter, or summer) is chosen from today's date. The planting advice itself comes from **gemma3:4b** running on your machine through [Ollama](https://ollama.com), not from a paid cloud API.

## Why open-source AI fits

- **Free to run.** After you download Ollama and the model once, each question costs nothing. There is no API key and no per-token bill.
- **Offline.** The Flask app talks to `http://localhost:11434`. You do not need the internet for advice after setup (the model and this app are both local).
- **Private.** Your city never leaves your computer. A garden planner is a good place for that: location is personal, and a closed API would send it to someone else's server.

That is the point of this project: get people *off* the screen and into a real garden, with a model that can live on a laptop.

## Season map (India)

| Months | Season used |
| --- | --- |
| March–May | summer |
| June–September | monsoon |
| October–February | winter |

The model is asked to tailor crops to that season and the city you typed.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- The `gemma3:4b` model pulled locally

## How to run it

From this folder, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull gemma3:4b
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

If Ollama is not already running, start it (the Ollama app, or `ollama serve`) before you click the button. The first answer can take a while while the model loads into memory.

On macOS or Linux, activate the venv with `source .venv/bin/activate` instead.

## How it works

1. The browser posts the city to `/plant`.
2. Flask maps today's month to monsoon, winter, or summer.
3. Flask calls Ollama's `/api/generate` with `stream: false` so the UI gets one complete answer.
4. The page shows the season and the model's planting advice.
