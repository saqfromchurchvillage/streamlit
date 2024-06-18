import streamlit as st
import csv
import os

# Tiedoston nimi
csv_file = 'olut_ranking.csv'

# Alusta CSV-tiedosto, jos se ei ole olemassa
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Oluen nimi", "Arvostelija", "Tyyppi", "Arvosana"])

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
        # Kirjoita uusi arvostelu suoraan CSV-tiedostoon
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([beer_name, arvostelijan_nimi, beer_type, rating])
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

# Näytä kaikki arvostelut
st.subheader("Kaikki arvostelut")
if os.path.exists(csv_file):
    reviews = pd.read_csv(csv_file)
    st.markdown(reviews.to_html(classes='wide-table', index=False), unsafe_allow_html=True)

st.empty()
st.empty()

# Top 5 oluet
st.subheader("Top 5 Oluet")
if os.path.exists(csv_file):
    reviews = pd.read_csv(csv_file)
    top_beers = reviews.groupby(["Oluen nimi", "Tyyppi"]).agg(Keskiarvo=("Arvosana", "mean"), Arvosteluja=("Arvosana", "count")).reset_index()
    top_beers = top_beers.sort_values(by="Keskiarvo", ascending=False).head(5)
    top_beers_html = top_beers.to_html(classes='wide-table', index=False)
    st.markdown(top_beers_html, unsafe_allow_html=True)

st.empty()

# Keskiarvoarvosana per olut
st.subheader("Keskiarvoarvosana per Olut")
if os.path.exists(csv_file):
    reviews = pd.read_csv(csv_file)
    average_ratings = reviews.groupby("Oluen nimi")["Arvosana"].mean().reset_index()
    fig, ax = plt.subplots()
    ax.barh(average_ratings["Oluen nimi"], average_ratings["Arvosana"], color='skyblue')
    ax.set_xlabel("Keskiarvo")
    ax.set_title("Keskiarvoarvosana per Olut")
    st.pyplot(fig)

st.empty()
st.empty()

# Arvostelujen jakauma
st.subheader("Arvostelujen jakauma")
if os.path.exists(csv_file):
    reviews = pd.read_csv(csv_file)
    rating_counts = reviews["Arvosana"].value_counts().sort_index()
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

# Arvostelijakohtaiset arvosanat
st.subheader("Arvostelijakohtaiset arvosanat")
if os.path.exists(csv_file):
    reviews = pd.read_csv(csv_file)
    pivot_table = reviews.pivot_table(index="Oluen nimi", columns="Arvostelija", values="Arvosana", aggfunc='mean')
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu", cbar=True, ax=ax)
    ax.set_title("Arvostelijakohtaiset arvosanat")
    st.pyplot(fig)
