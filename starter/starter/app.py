"""My Festival REST API — M10 starter (CSC Rahti).

FI: Tämä on M10-tehtävän lähtöpohja. GET /api/artists on valmiina mallina;
    toteuta loput TODO-kohdat. Aja paikallisesti:  python app.py
    ja testaa:  python test_endpoints.py http://localhost:8080
EN: This is the M10 starter. GET /api/artists is done as an example;
    implement the remaining TODOs. Run locally:  python app.py
    and test:  python test_endpoints.py http://localhost:8080
"""
import os
import re
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

app = Flask(__name__)

# FI: Kanta kulkee kontin mukana. Polun voi vaihtaa ympäristömuuttujalla.
# EN: The database ships inside the container. Override the path with an env var.
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "myfestival.db"))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # M8: sqlite3 ei valvo FK:ita oletuksena / FKs are off by default
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def health():
    """FI: Rahti ja selain näkevät, että sovellus on pystyssä.
    EN: Lets Rahti and your browser see the app is up."""
    return jsonify(status="ok", endpoints=["/api/artists", "/api/days", "/api/stages",
                                           "/api/artists/<id>/events", "/api/timetable?day=YYYY-MM-DD",
                                           "POST /api/events", "DELETE /api/events/<id>"])


@app.get("/api/artists")
def get_artists():
    conn = get_db()
    rows = conn.execute("SELECT artist_id, name, country FROM Artist ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/days")
def get_days():
    """FI: Apuendpoint: festivaalipäivät (tarkistin hakee tästä day_id:n).
    EN: Helper endpoint: festival days (the checker reads day_id from here)."""
    conn = get_db()
    rows = conn.execute("SELECT day_id, date FROM Day ORDER BY date").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/stages")
def get_stages():
    """FI: Apuendpoint: lavat. EN: Helper endpoint: stages."""
    conn = get_db()
    rows = conn.execute("SELECT stage_id, name FROM Stage ORDER BY stage_id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/artists/<int:artist_id>/events")
def get_artist_events(artist_id):
    conn = get_db()
    # Tuntematon artisti → 404
    artist = conn.execute(
        "SELECT artist_id FROM Artist WHERE artist_id = ?", (artist_id,)
    ).fetchone()
    if artist is None:
        conn.close()
        return jsonify(error="Artist not found"), 404

    rows = conn.execute("""
        SELECT e.event_id,
               d.date AS day,
               s.name AS stage,
               e.start_time AS starts
        FROM Event e
        JOIN Day d   ON e.day_id = d.day_id
        JOIN Stage s ON e.stage_id = s.stage_id
        WHERE e.artist_id = ?
        ORDER BY e.start_time
    """, (artist_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/timetable")
def get_timetable():
    day = request.args.get("day")  # kyselyparametri ?day=YYYY-MM-DD
    conn = get_db()

    if day is not None:
        # Virheellinen päivämäärämuoto → 400
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
            conn.close()
            return jsonify(error="Invalid date format. Use YYYY-MM-DD"), 400

        rows = conn.execute("""
            SELECT d.date,
                   s.name AS stage,
                   a.name AS artist,
                   e.start_time AS starts,
                   e.end_time   AS ends
            FROM Event e
            JOIN Day d   ON e.day_id = d.day_id
            JOIN Stage s ON e.stage_id = s.stage_id
            JOIN Artist a ON e.artist_id = a.artist_id
            WHERE d.date = ?
            ORDER BY e.start_time
        """, (day,)).fetchall()
    else:
        # Ilman parametria → koko ohjelma
        rows = conn.execute("""
            SELECT d.date,
                   s.name AS stage,
                   a.name AS artist,
                   e.start_time AS starts,
                   e.end_time   AS ends
            FROM Event e
            JOIN Day d   ON e.day_id = d.day_id
            JOIN Stage s ON e.stage_id = s.stage_id
            JOIN Artist a ON e.artist_id = a.artist_id
            ORDER BY d.date, e.start_time
        """).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])


@app.post("/api/events")
def create_event():
    body = request.get_json(silent=True) or {}

    # Pakolliset kentät
    required = ["artist_id", "stage_id", "day_id", "start_dt"]
    missing = [k for k in required if k not in body or body[k] is None]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    artist_id = body["artist_id"]
    stage_id = body["stage_id"]
    day_id = body["day_id"]
    start_dt = str(body["start_dt"])

    # start_dt-muoto YYYY-MM-DD HH:MM:SS
    if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", start_dt):
        return jsonify(error="start_dt must be in format YYYY-MM-DD HH:MM:SS"), 400

    try:
        start = datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
        end = start + timedelta(minutes=45)
        # Kannassa on start_time / end_time muodossa HH:MM tai HH:MM:SS
        start_time = start.strftime("%H:%M:%S")
        end_time = end.strftime("%H:%M:%S")
    except ValueError:
        return jsonify(error="Invalid start_dt value"), 400

    # event_type_id = 1 (Concert) – lähin vastine 'performance':lle
    event_type_id = 1

    conn = get_db()
    try:
        cur = conn.execute("""
            INSERT INTO Event (artist_id, stage_id, day_id, event_type_id, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (artist_id, stage_id, day_id, event_type_id, start_time, end_time))
        conn.commit()
        event_id = cur.lastrowid

        row = conn.execute(
            "SELECT * FROM Event WHERE event_id = ?", (event_id,)
        ).fetchone()
        conn.close()
        return jsonify(dict(row)), 201
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify(error=f"Integrity error: {str(e)}"), 400


@app.delete("/api/events/<int:event_id>")
def delete_event(event_id):
    conn = get_db()
    cur = conn.execute("DELETE FROM Event WHERE event_id = ?", (event_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()

    if deleted == 0:
        return jsonify(error="Event not found"), 404
    return "", 204   # tyhjä runko + 204 No Content


if __name__ == "__main__":
    # FI: Paikallinen kehityspalvelin. Rahdissa sovellusta ajaa gunicorn (ks. Dockerfile).
    # EN: Local dev server. On Rahti the app is run by gunicorn (see Dockerfile).
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)

if __name__ == "__main__":
    # FI: Paikallinen kehityspalvelin. Rahdissa sovellusta ajaa gunicorn (ks. Dockerfile).
    # EN: Local dev server. On Rahti the app is run by gunicorn (see Dockerfile).
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
