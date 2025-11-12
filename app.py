import streamlit as st
import pickle
import pandas as pd
import requests
import os

# --- NEW DOWNLOAD LOGIC ---
# HERE ARE THE VARIABLES YOU WERE LOOKING FOR:

MOVIES_URL = "https://huggingface.co/WaqarAhmadRiaz/Movie_recommender_system/resolve/main/movie_dict.pkl"
MOVIES_PATH = "movie_dict.pkl"

SIMILARITY_URL = "https://huggingface.co/WaqarAhmadRiaz/Movie_recommender_system/resolve/main/similarity.pkl"
SIMILARITY_PATH = "similarity.pkl"

# --- End of link section ---


def download_file(url, path, file_name):
    """Downloads a file if it doesn't exist."""
    if not os.path.exists(path):
        st.info(f"Downloading {file_name}... This may take a moment.")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status() # Check for HTTP errors
            
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success(f"{file_name} downloaded successfully!")
        except Exception as e:
            st.error(f"Error downloading {file_name}: {e}")
            st.error(f"Please double-check your Hugging Face URL for {file_name}.")
            st.stop()
    else:
        print(f"{file_name} already exists.")


def fetch_poster(movie_id):
    """Fetches a movie poster from the TMDB API."""
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=b7de28b07642145fd0cbff54321102e5&language=en-US')
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://placehold.co/500x750/333333/FFFFFF?text=No+Poster"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "https://placehold.co/500x750/333333/FFFFFF?text=Error"

def recommend(movie):
    """Recommends 5 similar movies."""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], []
        
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# --- MODIFIED LOADING SECTION ---
# This section now downloads the files first.

download_file(MOVIES_URL, MOVIES_PATH, "movie dictionary")
try:
    movies_dict = pickle.load(open(MOVIES_PATH, 'rb'))
    movies = pd.DataFrame(movies_dict)
except Exception as e:
    st.error(f"Error loading {MOVIES_PATH}: {e}")
    st.stop()

download_file(SIMILARITY_URL, SIMILARITY_PATH, "recommendation model")
try:
    similarity = pickle.load(open(SIMILARITY_PATH, 'rb'))
except Exception as e:
    st.error(f"Error loading {SIMILARITY_PATH}: {e}")
    st.stop()
# --- END OF LOADING SECTION ---


# --- STREAMLIT APP LAYOUT ---
st.title('Movie Recommendation System')

selected_movie_name = st.selectbox('Select a movie you like:', movies['title'].values)

if st.button('Recommend'):
    with st.spinner("Finding recommendations..."):
        names, posters = recommend(selected_movie_name)
    
    if names:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(names[0])
            st.image(posters[0])
        with col2:
            st.text(names[1])
            st.image(posters[1])
        with col3:
            st.text(names[2])
            st.image(posters[2])
        with col4:
            st.text(names[3])
            st.image(posters[3])
        with col5:
            st.text(names[4])
            st.image(posters[4])