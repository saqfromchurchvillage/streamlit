import streamlit as st
import pandas as pd
import os

# Tiedoston nimi
csv_file = 'olut_ranking.csv'

# Lue olemassa olevat arvostelut CSV-tiedostosta tai luo tyhjä DataFrame
if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
    st.session_state.reviews = pd.read_csv(csv_file)
else:
    st.session_state.reviews = pd.DataFrame(columns=["Oluen nimi", "Arvostelija", "Tyyppi", "Arvosana"])

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

rating = st.sidebar.slider("Rating", 1.0, 5.0, 2.5)

if st.sidebar.button("Submit"):
    if beer_name and beer_name != "Lisää uusi olut" and arvostelijan_nimi:
        new_review = pd.DataFrame({"Oluen nimi": [beer_name], "Arvostelija": [arvostelijan_nimi], "Tyyppi": [beer_type], "Rating": [rating]})
        st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], ignore_index=True)
        st.session_state.reviews.to_csv(csv_file, index=False)
        st.sidebar.success("Arvostelu tallennettu!")
    else:
        st.sidebar.warning("Muista lisätä oluen nimi, tyyppi ja arvostelijan nimi.")

# Display all reviews
st.subheader("Kaikki arvostelut")
st.dataframe(st.session_state.reviews)

# Top 5 beers
st.subheader("Top 5 Oluet")
top_beers = st.session_state.reviews.groupby("Oluen nimi").agg(Keskiarvo=("Rating", "mean"), Arvosteluja=("Rating", "count")).reset_index()
top_beers = top_beers.sort_values(by="Keskiarvo", ascending=False).head(5)
st.table(top_beers)

# Average ratings per beer
st.subheader("Keskiarvo Rating per Olut")
average_ratings = st.session_state.reviews.groupby("Oluen nimi")["Rating"].mean().reset_index()
fig, ax = plt.subplots()
ax.barh(average_ratings["Oluen nimi"], average_ratings["Rating"], color='skyblue')
ax.set_xlabel("Ke
