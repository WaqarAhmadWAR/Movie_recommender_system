import streamlit as st
import pickle
import pandas as pd
import requests
import os # <-- Make sure this is imported

# --- NEW DOWNLOAD LOGIC ---

# I have added your Google Drive link here.
SIMILARITY_URL = "https://drive.google.com/uc?id=1MwnezfDihkS-cUmjvTxWRG0Vu52vnXyN"
SIMILARITY_PATH = "similarity.pkl"

def download_file(url, path, file_name):
    """Downloads a file if it doesn't exist."""
    if not os.path.exists(path):
        st.info(f"Downloading {file_name}... This may take a moment (it's 176MB).")
        try:
            # Use stream=True for large files
            response = requests.get(url, stream=True)
            response.raise_for_status() # Check for HTTP errors
            
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success(f"{file_name} downloaded successfully!")
        except Exception as e:
            # Show a specific error if the download fails
            st.error(f"Error downloading {file_name}: {e}")
            st.error("Please check the Google Drive link and sharing permissions.")
            st.stop() # Stop the app if it can't download
    else:
        # This will print to your Streamlit log, not the app
        print(f"{file_name} already exists.")
# --- END OF NEW LOGIC ---


def fetch_poster(movie_id):
    """Fetches a movie poster from the TMDB API."""
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=b7de28b07642145fd0cbff54321102e5&language=en-US')
        response.raise_for_status() # Check for API errors
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            # Return a placeholder if no poster is found
            return "https://placehold.co/500x750/333333/FFFFFF?text=No+Poster"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        # Return a placeholder on error
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
        # fetch poster from API
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# --- MODIFIED LOADING SECTION ---

# This file is in your GitHub repo, so it loads normally.
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
except Exception as e:
    st.error(f"Error loading movie_dict.pkl: {e}")
    st.stop()

# This file is too big for GitHub, so we download it first.
# The download_file function will run, and then we load the file.
download_file(SIMILARITY_URL, SIMILARITY_PATH, "recommendation model")
try:
    similarity = pickle.load(open(SIMILARITY_PATH, 'rb'))
except Exception as e:
    st.error(f"Error loading similarity.pkl: {e}")
    st.stop()
# --- END OF LOADING SECTION ---


# --- STREAMLIT APP LAYOUT ---
st.title('Movie Recommendation System')

# Use the movie titles from the dataframe for the selectbox
selected_movie_name = st.selectbox('Select a movie you like:', movies['title'].values)

if st.button('Recommend'):
    with st.spinner("Finding recommendations..."):
        names, posters = recommend(selected_movie_name)
    
    if names: # Check if recommendations were found
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(names[0])
            st.image(posters[0])
        with col2:
            st.text(names[1])
            st.image(posts[1])
        with col3:
            st.text(names[2])
            st.image(posters[2])
        with col4:
            st.text(names[3])
            st.image(posters[3])
        with col5:
            st.text(names[4])
            st.image(posters[4])