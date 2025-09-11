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
            SELECT id, title, poster_url, backdrop_url, genres, overview
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
            "overview": row[5] if len(row) > 5 and row[5] is not None else "Pas de description disponible."
        }

    return render_template("film.html", film=film)

if __name__ == "__main__":
    app.run(debug=True)
