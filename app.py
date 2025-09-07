import streamlit as st
import pickle
import pandas as pd
import requests

# Replace with your OMDb API key (keep inside quotes!)
OMDB_API_KEY = "49a5009a"

def create_placeholder_url(text):
    """Create a placeholder image if poster not found"""
    return f"https://via.placeholder.com/500x750/1e293b/f1f5f9?text={text.replace(' ', '+')}"

def fetch_poster(movie_title):
    """Fetch movie poster from OMDb API with fallback"""
    try:
        # Try exact title match first
        url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("Poster") and data["Poster"] != "N/A":
            return data["Poster"]

        # If not found, try search mode
        search_url = f"http://www.omdbapi.com/?s={movie_title}&apikey={OMDB_API_KEY}"
        search_response = requests.get(search_url, timeout=5).json()
        if "Search" in search_response:
            return search_response["Search"][0].get("Poster", create_placeholder_url("No Poster"))

        return create_placeholder_url("No Poster")

    except Exception as e:
        print(f"Error fetching poster for {movie_title}: {e}")
        return create_placeholder_url("Error")

def recommend(movie):
    """Generate movie recommendations with posters and scores"""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        similarity_scores = []
        posters = []

        for i in movies_list:
            movie_title = movies.iloc[i[0]].title
            score = round(i[1] * 100, 1)

            recommended_movies.append(movie_title)
            similarity_scores.append(score)
            posters.append(fetch_poster(movie_title))

        return recommended_movies, similarity_scores, posters

    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return [], [], []

# Load data
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Streamlit UI
st.title('🎬 Movie Recommender System')
st.markdown("Select a movie from the dropdown to get personalized recommendations!")

selected_movie_name = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Show Recommendation', type='primary'):
    with st.spinner('🎬 Finding similar movies for you...'):
        names, scores, posters = recommend(selected_movie_name)

        if names and scores:
            st.success(f"Here are 5 movies similar to **{selected_movie_name}**:")

            for i, (name, score, poster) in enumerate(zip(names, scores, posters)):
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(poster, width=150)
                with col2:
                    st.subheader(f"#{i+1} {name}")
                    st.write(f"Similarity: {score}%")
                    stars = "⭐" * min(5, int(score // 10))
                    st.write(stars)
                st.divider()
        else:
            st.error("No recommendations found.")


# Add some styling
st.markdown("""
<style>
    .stContainer > div {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }

    .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Add footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888;'>
        🎬 Movie recommendations powered by machine learning | 
        Poster data from <a href='https://www.themoviedb.org/' target='_blank'>TMDb</a>
    </div>
    """,
    unsafe_allow_html=True
)