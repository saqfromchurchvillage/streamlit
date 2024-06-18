import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Tiedoston nimi
csv_file = 'olut_ranking.csv'

# Lue olemassa olevat arvostelut CSV-tiedostosta tai luo tyhjä DataFrame
if os.path.exists(csv_file):
    try:
        st.session_state.reviews = pd.read_csv(csv_file)
    except pd.errors.EmptyDataError:
        st.session_state.reviews = pd.DataFrame(columns=["Oluen nimi", "Arvostelija", "Tyyppi", "Rating"])
else:
    st.session_state.reviews = pd.DataFrame(columns=["Oluen nimi", "Arvostelija", "Tyyppi", "Rating"])

if "beer_names" not in st.session_state:
    st.session_state.beer_names = ["Staropramen Lager", "Pilsner Urquell", "Budojovicky Budvar", "Postriziny Francinuv Lezak", "Krusovice Pale Lager", "Budejovicky 1795 Premium Lager", "Bernard Bohemiam Lager", "Lisää uusi olut"]

st.title("Tsekkioluiden ranking by Susilauma")

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

rating = st.sidebar.slider("Rating", 0.0, 5.0, 2.5, step=0.25)

if st.sidebar.button("Submit"):
    if beer_name and beer_name != "Lisää uusi olut" and arvostelijan_nimi:
        new_review = pd.DataFrame({"Oluen nimi": [beer_name], "Arvostelija": [arvostelijan_nimi], "Tyyppi": [beer_type], "Rating": [rating]})
        st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], ignore_index=True)
        st.session_state.reviews.to_csv(csv_file, index=False)
        st.sidebar.success("Arvostelu tallennettu!")
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
st.markdown(st.session_state.reviews.to_html(classes='wide-table'), unsafe_allow_html=True)

# Top 5 beers
st.subheader("Top 5 Oluet")
top_beers = st.session_state.reviews.groupby(["Oluen nimi", "Tyyppi"]).agg(Keskiarvo=("Rating", "mean"), Arvosteluja=("Rating", "count")).reset_index()
top_beers = top_beers.sort_values(by="Keskiarvo", ascending=False).head(5)

# Muuta DataFrame HTML:ksi ilman indeksiä
top_beers_html = top_beers.to_html(classes='wide-table')

# Näytä Top 5 oluet
st.markdown(top_beers_html, unsafe_allow_html=True)




# Average ratings per beer
st.subheader("Keskiarvo Rating per Olut")
average_ratings = st.session_state.reviews.groupby("Oluen nimi")["Rating"].mean().reset_index()
fig, ax = plt.subplots()
ax.barh(average_ratings["Oluen nimi"], average_ratings["Rating"], color='skyblue')
ax.set_xlabel("Keskiarvo Rating")
ax.set_title("Keskiarvo Rating per Olut")
st.pyplot(fig)

# Rating distribution
st.subheader("Arvostelujen jakauma")
rating_counts = st.session_state.reviews["Rating"].value_counts().sort_index()
fig, ax = plt.subplots()
ax.bar(rating_counts.index, rating_counts.values, color='lightgreen')
ax.set_xlabel("Rating")
ax.set_ylabel("Arvostelujen lukumäärä")
ax.set_title("Arvostelujen jakauma")
ax.yaxis.get_major_locator().set_params(integer=True)  # Show only integers on y-axis
st.pyplot(fig)

# Heatmap of ratings by reviewer and beer
st.subheader("Arvostelijakohtaiset arvosanat")
pivot_table = st.session_state.reviews.pivot_table(index="Oluen nimi", columns="Arvostelija", values="Rating", aggfunc='mean')
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu", cbar=True, ax=ax)
ax.set_title("Arvostelijakohtaiset arvosanat")
st.pyplot(fig)
