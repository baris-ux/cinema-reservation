from flask import Flask, render_template
import psycopg2

app = Flask(__name__)
DB_URL = "postgresql://postgres:root@127.0.0.1:5432/movies"

def get_movies():
    with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, poster_url, genres, backdrop_url
            FROM movies
            ORDER BY release_date DESC;
        """)
        rows = cur.fetchall()
        movies = [
            {
                "id": row[0],
                "title": row[1],
                "poster_url": row[2],
                "genres": row[3],
                "backdrop_url": row[4]
            }
            for row in rows
        ]
        return movies

@app.route("/")
def index():
    movies = get_movies()
    return render_template("index.html", movies=movies)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/film/<int:film_id>")
def film_detail(film_id):
    with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, poster_url, backdrop_url, genres, overview, runtime, release_date, trailer_youtube_id
            FROM movies
            WHERE id = %s;
        """, (film_id,))
        row = cur.fetchone()

        if not row:
            return abort(404, overview="Film introuvable")

        film = {
            "id": row[0],
            "title": row[1],
            "poster_url": row[2],
            "backdrop_url": row[3],
            "genres": row[4],
            "overview": row[5] if len(row) > 5 and row[5] is not None else "Pas de description disponible.",
            "runtime" : row[6],
            "release_date" : row[7],
            "trailer_youtube_id" : row[8],
        }

        cur.execute('SELECT DISTINCT cinema FROM seance WHERE movie_id = %s ORDER BY cinema;', (film_id,))
        cinemas = [r[0] for r in cur.fetchall()]

        cur.execute('SELECT DISTINCT date_seance FROM seance WHERE movie_id = %s ORDER BY date_seance;', (film_id,))
        dates = [r[0] for r in cur.fetchall()]

        cur.execute('SELECT DISTINCT langue FROM seance WHERE movie_id = %s ORDER BY langue;', (film_id,))
        langues = [r[0] for r in cur.fetchall()]

        
        cur.execute('SELECT DISTINCT format_projection FROM seance WHERE movie_id = %s ORDER BY format_projection;', (film_id,))
        formats = [r[0] for r in cur.fetchall()]


    return render_template(
        "film.html",
        film=film,
        cinemas=cinemas,
        dates=dates,
        langues=langues,
        formats=formats
        )


if __name__ == "__main__":
    app.run(debug=True)
