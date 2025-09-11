
from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

DB_URL = "postgresql://postgres:root@127.0.0.1:5432/movies"

def get_movies():
    with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute("SELECT title, poster_url FROM movies ORDER BY release_date DESC;")
        return cur.fetchall()    

@app.route("/")
def index():
    movies = get_movies()
    return render_template("index.html", movies=movies)

if __name__ == "__main__":
    app.run(debug=True)
