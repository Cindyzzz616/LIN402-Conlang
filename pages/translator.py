import json

import streamlit as st


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def looks_like_english_gloss(text):
    if not isinstance(text, str):
        return False
    markers = [" ", "/", "(", ")", ","]
    return any(marker in text for marker in markers)


def invert_if_needed(data):
    if not isinstance(data, dict):
        return {}

    items = [(k, v) for k, v in data.items() if isinstance(k, str) and isinstance(v, str)]
    if not items:
        return {}

    key_markers = sum(1 for k, _ in items if looks_like_english_gloss(k))
    val_markers = sum(1 for _, v in items if looks_like_english_gloss(v))
    if val_markers > key_markers:
        items = [(v, k) for k, v in items]
    elif key_markers == val_markers:
        avg_key_len = sum(len(k) for k, _ in items) / len(items)
        avg_val_len = sum(len(v) for _, v in items) / len(items)
        if avg_key_len < avg_val_len:
            items = [(v, k) for k, v in items]

    return dict(items)


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
eng_to_con.update({k.lower(): v.lower() for k, v in invert_if_needed(base).items()})
eng_to_con.update({k.lower(): v.lower() for k, v in invert_if_needed(roots).items()})
eng_to_con.update({k.lower(): v.lower() for k, v in invert_if_needed(function_words).items()})
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