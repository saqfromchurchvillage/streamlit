import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import base64
import io
from streamlit_tags import st_tags

# Tiedoston nimi
csv_file = 'olut_ranking.csv'
github_repo = 'saqfromchurchvillage/streamlit'
github_token = st.secrets["github_token"]  # Lisää tämä Streamlit-sekretiksi Streamlitin asetuksissa

def read_github_file(repo, file_path, token):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_content = response.json()['content']
        return base64.b64decode(file_content).decode('utf-8')
    else:
        return None

def write_github_file(repo, file_path, content, token, sha=None):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    data = {
        "message": "Update CSV file",
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha

    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 201 or response.status_code == 200

# Lue olemassa olevat arvostelut CSV-tiedostosta tai luo tyhjä DataFrame
csv_content = read_github_file(github_repo, csv_file, github_token)
if csv_content:
    try:
        reviews = pd.read_csv(io.StringIO(csv_content))
    except pd.errors.EmptyDataError:
        reviews = pd.DataFrame(columns=["Oluen nimi", "Arvostelija", "Tyyppi", "Arvosana"])
else:
    reviews = pd.DataFrame(columns=["Oluen nimi", "Arvostelija", "Tyyppi", "Arvosana"])

st.session_state.reviews = reviews

# Päivitä oluen nimet CSV-tiedostosta
if "beer_names" not in st.session_state:
    if not st.session_state.reviews.empty:
        st.session_state.beer_names = sorted(set(st.session_state.reviews['Oluen nimi'].tolist()))
    else:
        st.session_state.beer_names = []

st.title(":flag-cz: Tsekkioluiden ranking by Susilauma :wolf:")

# Sidebar for submitting reviews
st.sidebar.title("Arvioi olut")
arvostelijan_nimi = st.sidebar.text_input("Arvostelija")

# Käytä 'with st.sidebar:' -kontekstia
with st.sidebar:
    # Käytä st_tags komponenttia oluen nimen syöttämiseen
    beer_name_input = st_tags(
        label='Oluen nimi',
        text='Kirjoita oluen nimi ja valitse listasta tai lisää uusi',
        value=[],
        suggestions=st.session_state.beer_names,
        maxtags=1,  # Salli vain yksi nimi
        key='beer_name_tags'
    )

    if beer_name_input:
        beer_name = beer_name_input[0]  # Otetaan ensimmäinen (ja ainoa) syötetty nimi
        # Näytetään valittu oluen nimi
        st.markdown(f"**Valittu olut:** {beer_name}")
    else:
        beer_name = ""
        st.warning("Ole hyvä ja syötä oluen nimi.")

    beer_type = st.selectbox("Valitse oluen tyyppi", ["0,5 l tölkki", "0,33 l tölkki", "0,33 l lasipullo", "0,5 l lasipullo", "hanaolut"])

    rating = st.slider("Arvosana", 0.0, 5.0, 2.5, step=0.25)

    if st.button("Submit"):
        if beer_name and arvostelijan_nimi:
            new_review = pd.DataFrame({"Oluen nimi": [beer_name], "Arvostelija": [arvostelijan_nimi], "Tyyppi": [beer_type], "Arvosana": [rating]})
            st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], ignore_index=True)
            csv_updated_content = st.session_state.reviews.to_csv(index=False)
            
            # Päivitä oluen nimet, jos uusi olut lisätty
            if beer_name not in st.session_state.beer_names:
                st.session_state.beer_names.append(beer_name)
                st.session_state.beer_names.sort()
            
            # Getting SHA of the existing file
            sha_url = f"https://api.github.com/repos/{github_repo}/contents/{csv_file}"
            sha_response = requests.get(sha_url, headers={"Authorization": f"token {github_token}"})
            sha = sha_response.json().get("sha")
            
            if write_github_file(github_repo, csv_file, csv_updated_content, github_token, sha):
                st.success("Arvostelu tallennettu!")
            else:
                st.error("Virhe tallennettaessa GitHubiin.")
        else:
            st.warning("Muista lisätä oluen nimi ja arvostelijan nimi.")

# CSS for widening table cells
st.markdown(
    """
    <style>
    .dataframe th, .dataframe td {
        width: auto !important;
        min-width: 150px !important;
    }
    .wide-table {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True
)

# Loput koodistasi pysyy samana...

