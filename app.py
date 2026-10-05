import pickle
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry




TMDB_API_KEY = "bf9200b638344489e74d98f8bbcf5170"



session = requests.Session()

retry = Retry(
    total=3,
    connect=3,
    read=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("https://", adapter)
session.mount("http://", adapter)


def fetch_poster(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    try:
        response = session.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        poster_path = data.get("poster_path")

        if not poster_path:
            return None

        return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except requests.exceptions.RequestException as e:
        st.warning(f"Unable to fetch poster for movie ID {movie_id}.")
        print(f"TMDB request error: {e}")
        return None




def recommend(movie):

    index = movies[movies["title"] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:

        movie_id = movies.iloc[i[0]]["movie_id"]

        poster = fetch_poster(movie_id)

        recommended_movie_names.append(
            movies.iloc[i[0]]["title"]
        )

        recommended_movie_posters.append(poster)

    return recommended_movie_names, recommended_movie_posters



movies = pickle.load(
    open("model/movies_list.pkl", "rb")
)

similarity = pickle.load(
    open("model/similarity.pkl", "rb")
)


st.title("Movie Content-Based Recommender System")

movie_list = movies["title"].values

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)


if st.button("Show Recommendation"):

    recommended_movie_names, recommended_movie_posters = recommend(
        selected_movie
    )

    cols = st.columns(5)

    for i, col in enumerate(cols):

        with col:

            st.write(
                recommended_movie_names[i]
            )

            poster = recommended_movie_posters[i]

            if poster:
                st.image(
                    poster,
                    use_container_width=True
                )
            else:
                st.info("Poster unavailable")
