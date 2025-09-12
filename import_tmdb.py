import os, requests, psycopg2
from dotenv import load_dotenv
load_dotenv()

TMDB = os.getenv("TMDB_API_KEY")
DB   = os.getenv("DATABASE_URL")

def img(path, size="w500"):
    return f"https://image.tmdb.org/t/p/{size}{path}" if path else None

def upsert_movie(tmdb_id: int):
    m = requests.get(
        f"https://api.themoviedb.org/3/movie/{tmdb_id}",
        params={"api_key": TMDB, "language": "fr-FR"}
    ).json()
    genres   = [g["name"] for g in m.get("genres", [])]
    poster   = img(m.get("poster_path"), "w500")
    backdrop = img(m.get("backdrop_path"), "w780")

    trailer_key = get_trailer_key(tmdb_id)

    conn = psycopg2.connect(DB)
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO movies (tmdb_id, title, overview, release_date, runtime, poster_url, backdrop_url, genres, trailer_youtube_id)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
      ON CONFLICT (tmdb_id) DO UPDATE SET
        title=EXCLUDED.title,
        overview=EXCLUDED.overview,
        release_date=EXCLUDED.release_date,
        runtime=EXCLUDED.runtime,
        poster_url=EXCLUDED.poster_url,
        backdrop_url=EXCLUDED.backdrop_url,
        genres=EXCLUDED.genres,
        trailer_youtube_id=EXCLUDED.trailer_youtube_id
      RETURNING id, title, trailer_youtube_id;
    """, (m["id"], m.get("title"), m.get("overview"), m.get("release_date"),
          m.get("runtime"), poster, backdrop, genres, trailer_key))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    print("Import OK →", row)

def get_trailer_key(tmdb_id: int, lang="fr-FR"):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
    resp = requests.get(url, params={"api_key": TMDB, "language": lang})
    data = resp.json()
    videos = data.get("results", [])

    for v in videos:
        if v.get("site") == "YouTube" and v.get("type") == "Trailer":
            return v['key']

def import_by_title(query: str):
    print("DEBUG TMDB_API_KEY present:", bool(TMDB))
    resp = requests.get(
        "https://api.themoviedb.org/3/search/movie",
        params={"api_key": TMDB, "language": "fr-FR", "query": query}
    )
    print("DEBUG status:", resp.status_code)
    try:
        payload = resp.json()
    except Exception as e:
        print("DEBUG invalid JSON:", e, "body:", resp.text[:300])
        return

    # Si TMDb renvoie une erreur, elle est dans status_code/status_message
    if payload.get("success") is False or ("status_code" in payload and "results" not in payload):
        print("TMDb ERROR:", payload)
        return

    results = payload.get("results", [])
    print("DEBUG nb results:", len(results))
    if not results:
        print("DEBUG body:", str(payload)[:400])
        print("Aucun résultat")
        return

    first = results[0]
    print(f"Sélection: {first['title']} ({first.get('release_date','?')}) id={first['id']}")
    upsert_movie(first["id"])


if __name__ == "__main__":
    import_by_title("dune")  # entrer le nom du film
