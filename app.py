
from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

DB_URL = "postgresql://postgres:root@127.0.0.1:5432/movies"

def get_movies():
    with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute("SELECT title, poster_url, genres, backdrop_url FROM movies ORDER BY release_date DESC;")
        rows = cur.fetchall()  

        movies = [
            {
                "title": row[0],
                "poster_url": row[1],
                "genres": row[2],
                "backdrop_url": row[3]
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

if __name__ == "__main__":
    app.run(debug=True)
