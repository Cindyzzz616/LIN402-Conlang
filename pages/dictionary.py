import json

import streamlit as st


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def looks_like_english_gloss(text):
    if not isinstance(text, str):
        return False
    markers = [" ", "/", "(", ")", ","]
    return any(m in text for m in markers)


def is_inverted_mapping(data):
    # Detect orientation for simple dict[str, str]:
    # old: english -> conlang, new: conlang -> english
    items = [(k, v) for k, v in data.items() if isinstance(k, str) and isinstance(v, str)]
    if not items:
        return False

    key_markers = sum(1 for k, _ in items if looks_like_english_gloss(k))
    val_markers = sum(1 for _, v in items if looks_like_english_gloss(v))
    if val_markers > key_markers:
        return True
    if key_markers > val_markers:
        return False

    avg_key_len = sum(len(k) for k, _ in items) / len(items)
    avg_val_len = sum(len(v) for _, v in items) / len(items)
    return avg_key_len < avg_val_len


def normalize_compound_entry(k, data):
    # old schema:
    #   english -> {"lemma": "...", "roots": {english: lemma}}
    # new schema:
    #   lemma -> {"meaning": "...", "roots": {lemma: english}}
    if not isinstance(data, dict):
        return None

    if "lemma" in data:
        english = data.get("meaning", k)
        conlang = data.get("lemma", "")
        category = data.get("syntactic_category", "")
    else:
        english = data.get("meaning", "")
        conlang = k
        category = data.get("syntactic_category", "")

    if isinstance(english, list):
        english = ", ".join(english)
    return {"Type": "Compound", "English": english, "Conlang": conlang, "Category": category}


st.title("Dictionary")
st.caption("Browse generated entries and compounds.")

roots = load_json("roots.json")
compounds = load_json("compound_words.json")
function_words = load_json("function_words.json")

if not roots and not compounds and not function_words:
    st.info("No dictionary data found. Go to the `Create Words` page first.")
    st.stop()

english_query = st.text_input("English lookup").strip()
conlang_query = st.text_input("Conlang lookup").strip()
english_query_l = english_query.lower()
conlang_query_l = conlang_query.lower()

rows = []
if roots:
    roots_inverted = is_inverted_mapping(roots)
    for k, v in roots.items():
        eng, con = (v, k) if roots_inverted else (k, v)
        rows.append({"Type": "Base", "English": eng, "Conlang": con, "Category": ""})

if function_words:
    function_inverted = is_inverted_mapping(function_words)
    for k, v in function_words.items():
        eng, con = (v, k) if function_inverted else (k, v)
        rows.append({"Type": "Function", "English": eng, "Conlang": con, "Category": ""})

if compounds:
    for k, data in compounds.items():
        row = normalize_compound_entry(k, data)
        if row:
            rows.append(row)

if english_query_l:
    rows = [r for r in rows if english_query_l in r["English"].lower()]
if conlang_query_l:
    rows = [r for r in rows if conlang_query_l in r["Conlang"].lower()]

rows = sorted(rows, key=lambda r: (r["English"].lower(), r["Conlang"].lower()))

st.write(f"Entries: {len(rows)}")
st.dataframe(rows, use_container_width=True, hide_index=True)

if english_query_l and not rows:
    st.warning(f"No results for English word: `{english_query}`")
    st.write("Do you want to generate this word in the conlang?")
    if st.button("Yes, go to Create Words"):
        st.query_params["new_word"] = english_query
        st.switch_page("pages/create_words.py")
