import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import base64
import io

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

if "beer_names" not in st.session_state:
    st.session_state.beer_names = ["Staropramen Lager", "Pilsner Urquell", "Budojovicky Budvar", "Postriziny Francinuv Lezak", "Krusovice Pale Lager", "Budejovicky 1795 Premium Lager", "Bernard Bohemiam Lager", "Lisää uusi olut"]

st.title(":flag-cz: Tsekkioluiden ranking by Susilauma :wolf:")

# Sidebar for submitting reviews
st.sidebar.title("Arvioi olut")
arvostelijan_nimi = st.sidebar.text_input("Arvostelija")

beer_name_option = st.sidebar.selectbox("Valitse oluen nimi", st.session_state.beer_names)

if beer_name_option == "Lisää uusi olut":
    new_beer_name = st.sidebar.text_input("Lisää uusi olut")
    if st.sidebar.button("Lisää oluen nimi"):
        if new_beer_name and new_beer_name not in st.session_state.beer_names:
            st.session_state.beer_names.append(new_beer_name)
            st.sidebar.success(f"{new_beer_name} lisätty olutlistaan!")
        else:
            st.sidebar.warning("Virhe: olisikohan tuo nimi jo listassa? Hmmh...")
    beer_name = new_beer_name
else:
    beer_name = beer_name_option

beer_type = st.sidebar.selectbox("Valitse oluen tyyppi", ["0,5 l tölkki", "0,33 l tölkki", "0,33 l lasipullo", "0,5 l lasipullo", "hanaolut"])

rating = st.sidebar.slider("Arvosana", 0.0, 5.0, 2.5, step=0.25)

if st.sidebar.button("Submit"):
    if beer_name and beer_name != "Lisää uusi olut" and arvostelijan_nimi:
        new_review = pd.DataFrame({"Oluen nimi": [beer_name], "Arvostelija": [arvostelijan_nimi], "Tyyppi": [beer_type], "Arvosana": [rating]})
        st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], ignore_index=True)
        csv_updated_content = st.session_state.reviews.to_csv(index=False)
        
        # Getting SHA of the existing file
        sha_url = f"https://api.github.com/repos/{github_repo}/contents/{csv_file}"
        sha_response = requests.get(sha_url, headers={"Authorization": f"token {github_token}"})
        sha = sha_response.json().get("sha")
        
        if write_github_file(github_repo, csv_file, csv_updated_content, github_token, sha):
            st.sidebar.success("Arvostelu tallennettu!")
        else:
            st.sidebar.error("Virhe tallennettaessa GitHubiin.")
    else:
        st.sidebar.warning("Muista lisätä oluen nimi, tyyppi ja arvostelijan nimi.")

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

# Display all reviews
st.subheader("Kaikki arvostelut")
st.markdown(st.session_state.reviews.to_html(classes='wide-table', index=False), unsafe_allow_html=True)

st.empty()
st.empty()

# Top 5 beers
st.subheader("Top 5 Oluet")
top_beers = st.session_state.reviews.groupby("Oluen nimi").agg(Keskiarvo=("Arvosana", "mean"), Arvosteluja=("Arvosana", "count")).reset_index()
top_beers = top_beers.sort_values(by="Keskiarvo", ascending=False).head(5)

# Muuta DataFrame HTML:ksi ilman indeksiä
top_beers_html = top_beers.to_html(classes='wide-table', index=False)

# Näytä Top 5 oluet
st.markdown(top_beers_html, unsafe_allow_html=True)

st.empty()


# Average ratings per beer
st.subheader("Keskiarvoarvosana per Olut")
average_ratings = st.session_state.reviews.groupby("Oluen nimi")["Arvosana"].mean().reset_index()
fig, ax = plt.subplots()
ax.barh(average_ratings["Oluen nimi"], average_ratings["Arvosana"], color='skyblue')
ax.set_xlabel("Keskiarvo")
ax.set_title("Keskiarvoarvosana per Olut")
st.pyplot(fig)

st.empty()
st.empty()

# Rating distribution
st.subheader("Arvostelujen jakauma")
rating_counts = st.session_state.reviews["Arvosana"].value_counts().sort_index()
fig, ax = plt.subplots()
bars = ax.bar(rating_counts.index, rating_counts.values, color='lightgreen', width=0.4)
ax.set_xticks([i for i in range(6)])  # Näytä luvut 0-5 x-akselilla
ax.set_xlim(-0.5, 5.5)  # Aseta x-akselin rajoitukset
ax.set_ylim(0, max(rating_counts.values, default=1) + 1)  # Aseta y-akselin rajoitukset
ax.set_xlabel("Arvosana")
ax.set_ylabel("Arvostelujen lukumäärä")
ax.set_title("Arvostelujen jakauma")
ax.yaxis.get_major_locator().set_params(integer=True)  # Näytä vain kokonaisluvut y-akselilla

st.pyplot(fig)

# Heatmap of ratings by reviewer and beer
st.subheader("Arvostelijakohtaiset arvosanat")
pivot_table = st.session_state.reviews.pivot_table(index="Oluen nimi", columns="Arvostelija", values="Arvosana", aggfunc='mean')
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu", cbar=True, ax=ax)
ax.set_title("Arvostelijakohtaiset arvosanat")
st.pyplot(fig)
