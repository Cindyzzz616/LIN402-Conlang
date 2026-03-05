import json

import streamlit as st


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


st.title("Translator")
st.caption("Translate word-by-word between English and generated conlang forms.")

base = load_json("lexicon_mapped.json")
compounds = load_json("compound_words.json")

eng_to_con = dict(base)
for eng, item in compounds.items():
    eng_to_con[eng] = item["lemma"]
con_to_eng = {v: k for k, v in eng_to_con.items()}

if not eng_to_con:
    st.info("No generated mapping found. Go to `Create Words` and generate first.")
    st.stop()

mode = st.radio("Direction", ["English -> Conlang", "Conlang -> English"], horizontal=True)
text = st.text_area("Input text", placeholder="Enter words separated by spaces")

if st.button("Translate", type="primary"):
    tokens = [t.strip().lower() for t in text.split() if t.strip()]
    out = []
    missing = []
    if mode == "English -> Conlang":
        for t in tokens:
            v = eng_to_con.get(t)
            if v:
                out.append(v)
            else:
                out.append(f"[{t}]")
                missing.append(t)
    else:
        for t in tokens:
            v = con_to_eng.get(t)
            if v:
                out.append(v)
            else:
                out.append(f"[{t}]")
                missing.append(t)

    st.subheader("Output")
    st.code(" ".join(out) if out else "", language="text")
    if missing:
        st.warning("Not found: " + ", ".join(sorted(set(missing))))
