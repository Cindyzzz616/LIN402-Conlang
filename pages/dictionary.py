import json

import streamlit as st


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


st.title("Dictionary")
st.caption("Browse generated entries and compounds.")

roots = load_json("roots.json")
compounds = load_json("compound_words.json")

if not roots and not compounds:
    st.info("No dictionary data found. Go to the `Create Words` page first.")
    st.stop()

english_query = st.text_input("English lookup").strip()
conlang_query = st.text_input("Conlang lookup").strip()
english_query_l = english_query.lower()
conlang_query_l = conlang_query.lower()

rows = []
if roots:
    for eng, con in roots.items():
        rows.append({"Type": "Base", "English": eng, "Conlang": con})
if compounds:
    for eng, data in compounds.items():
        rows.append({"Type": "Compound", "English": eng, "Conlang": data["lemma"]})

if english_query_l:
    rows = [r for r in rows if english_query_l in r["English"].lower()]
if conlang_query_l:
    rows = [r for r in rows if conlang_query_l in r["Conlang"].lower()]

st.write(f"Entries: {len(rows)}")
st.dataframe(rows, use_container_width=True, hide_index=True)

if english_query_l and not rows:
    st.warning(f"No results for English word: `{english_query}`")
    st.write("Do you want to generate this word in the conlang?")
    if st.button("Yes, go to Create Words"):
        st.query_params["new_word"] = english_query
        st.switch_page("pages/create_words.py")
