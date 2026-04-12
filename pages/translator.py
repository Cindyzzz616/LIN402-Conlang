import json
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent


def load_json(path):
    try:
        with (BASE_DIR / path).open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def looks_like_english_gloss(text):
    if not isinstance(text, str):
        return False
    markers = [" ", "/", "(", ")", ","]
    return any(marker in text for marker in markers)


def normalize_simple_mapping(data):
    if not isinstance(data, dict):
        return {}

    mapping = {}
    for left, right in data.items():
        if not isinstance(left, str):
            continue

        if isinstance(right, dict):
            forms = right.get("forms", {})
            if isinstance(forms, dict):
                for form, form_entry in forms.items():
                    if not isinstance(form, str) or not isinstance(form_entry, dict):
                        continue
                    english = form_entry.get("meaning")
                    if isinstance(english, list):
                        english = ", ".join(english)
                    if isinstance(english, str) and english:
                        mapping[english.lower()] = form.lower()
                continue

            english = right.get("meaning")
            if isinstance(english, list):
                english = ", ".join(english)
            if isinstance(english, str) and english:
                mapping[english.lower()] = left.lower()
            continue

        if not isinstance(right, str):
            continue

        left_english = looks_like_english_gloss(left)
        right_english = looks_like_english_gloss(right)

        if left_english and not right_english:
            english, conlang = left, right
        elif right_english and not left_english:
            english, conlang = right, left
        elif len(left) <= len(right):
            english, conlang = right, left
        else:
            english, conlang = left, right

        mapping[english.lower()] = conlang.lower()

    return mapping


def compound_to_mapping(data):
    mapping = {}
    if not isinstance(data, dict):
        return mapping

    for key, entry in data.items():
        if not isinstance(entry, dict):
            continue

        # Old schema: english -> {"lemma": "..."}
        if "lemma" in entry:
            english = key
            conlang = entry.get("lemma")
        # New schema: lemma -> {"meaning": "..."}
        else:
            english = entry.get("meaning")
            conlang = key

        if isinstance(english, list):
            english = ", ".join(english)
        if isinstance(english, str) and isinstance(conlang, str) and english and conlang:
            mapping[english.lower()] = conlang.lower()

    return mapping


st.title("Translator")
st.caption("Translate word-by-word between English and generated conlang forms.")

base = load_json("lexicon_mapped.json")
roots = load_json("roots.json")
function_words = load_json("function_words.json")
compounds = load_json("compound_words.json")

eng_to_con = {}
eng_to_con.update(normalize_simple_mapping(base))
eng_to_con.update(normalize_simple_mapping(roots))
eng_to_con.update(normalize_simple_mapping(function_words))
eng_to_con.update(compound_to_mapping(compounds))
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

st.header("Example")

st.markdown('''
| 3PL | Travel-N | Cloak-N | 3SG-POSS | Remove-IMP | Succeed-V | who-COMP | Person-N | strong-more-Adj | BE | that-COMP | Think-V | Should-T | that-COMP | Agree-V |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| hiko | netola | meluna | hin | lenui | pisu | wo | piha | maməlele | huhu | pu | neku | ti | pu | seku |
''')
