import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()
print("OMDB_API_KEY:", repr(os.getenv("OMDB_API_KEY")))
app = Flask(__name__, static_folder=".", static_url_path="")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
OMDB_BASE_URL = "https://www.omdbapi.com/"


def fetch_movie(title: str) -> dict:
    if not OMDB_API_KEY:
        return {"error": "OMDB_API_KEY is not set. Copy .env.example to .env and add your key."}

    response = requests.get(
        OMDB_BASE_URL,
        params={"apikey": OMDB_API_KEY, "t": title, "plot": "full"},
        timeout=10,
    )
    data = response.json()

    if response.status_code == 401 or data.get("Error") == "Invalid API key!":
        return {"error": "Invalid OMDb API key. Check OMDB_API_KEY in your .env file."}

    response.raise_for_status()

    if data.get("Response") == "False":
        return {"error": data.get("Error", "Movie not found.")}

    return {
        "title": data.get("Title"),
        "year": data.get("Year"),
        "rating": data.get("imdbRating"),
        "votes": data.get("imdbVotes"),
        "poster": data.get("Poster") if data.get("Poster") != "N/A" else None,
        "overview": data.get("Plot") if data.get("Plot") != "N/A" else None,
        "imdb_id": data.get("imdbID"),
        "genre": data.get("Genre"),
        "runtime": data.get("Runtime"),
    }


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.get("/api/movie")
def movie():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "Missing title parameter."}), 400

    try:
        result = fetch_movie(title)
    except requests.RequestException:
        return jsonify({"error": "Failed to reach OMDb. Try again later."}), 502

    if "error" in result:
        if "OMDB_API_KEY" in result["error"] or "Invalid OMDb API key" in result["error"]:
            status = 500
        else:
            status = 404
        return jsonify(result), status

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
