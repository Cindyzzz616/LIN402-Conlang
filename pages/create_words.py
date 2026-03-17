import json
import random

import streamlit as st


def load_inventory():
    with open("phonemic_inventory.json", encoding="utf-8") as f:
        return json.load(f)


def load_roots():
    try:
        with open("roots.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_compounds():
    try:
        with open("compound_words.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_roots(roots):
    with open("roots.json", "w", encoding="utf-8") as f:
        json.dump(roots, f, indent=2, ensure_ascii=False)


def is_lemma_taken(lemma):
    """Check if a lemma is already used in roots.json or compound_words.json"""
    roots = load_roots()
    compounds = load_compounds()

    if lemma in roots.keys() or lemma in roots.values():
        return True

    for compound_lemma, entry in compounds.items():
        if compound_lemma == lemma:
            return True
        if entry.get("lemma") == lemma:
            return True

    return False


def sanitize_pattern(pattern):
    return "".join(ch for ch in pattern.upper() if ch in {"C", "V"})


def generate_root(pattern, consonants, vowels):
    generated = []
    for symbol in pattern:
        if symbol == "C":
            generated.append(random.choice(consonants))
        elif symbol == "V":
            generated.append(random.choice(vowels))
    return "".join(generated)


def generate_unique_root(pattern, consonants, vowels, max_attempts=100):
    """Generate a root that is not already taken in roots.json or compound_words.json"""
    for _ in range(max_attempts):
        candidate = generate_root(pattern, consonants, vowels)
        if not is_lemma_taken(candidate):
            return candidate
    # If we can't find a unique one after max_attempts, return the last generated
    return candidate


st.title("Create Words")

if "root_pattern" not in st.session_state:
    st.session_state.root_pattern = ""
if "candidate_root" not in st.session_state:
    st.session_state.candidate_root = ""
if "manual_lemma" not in st.session_state:
    st.session_state.manual_lemma = ""

mode = st.radio("Choose what to create", ["Root", "Compound"], horizontal=True)

if mode == "Compound":
    st.info("Compound creation flow is ready for your next instructions.")
    st.stop()

inventory = load_inventory()
consonants = [p for p, v in inventory["phonemes"].items() if v["type"] == "consonant"]
vowels = [p for p, v in inventory["phonemes"].items() if v["type"] == "vowel"]

default_gloss = st.query_params.get("new_word", "")
gloss = st.text_input("English gloss (optional)", value=default_gloss).strip()

st.subheader("Lemma Input Method")
lemma_mode = st.radio("Choose how to create the lemma", ["Randomly generate", "Enter manually"], horizontal=True)

selected_lemma = ""

if lemma_mode == "Randomly generate":
    st.subheader("Syllable Structure")
    st.code(st.session_state.root_pattern if st.session_state.root_pattern else "(empty)", language="text")

    c_col, v_col, back_col, clear_col = st.columns(4)
    if c_col.button("C", key="btn_c"):
        st.session_state.root_pattern += "C"
        st.rerun()
    if v_col.button("V", key="btn_v"):
        st.session_state.root_pattern += "V"
        st.rerun()
    if back_col.button("Backspace", key="btn_back"):
        st.session_state.root_pattern = st.session_state.root_pattern[:-1]
        st.rerun()
    if clear_col.button("Clear", key="btn_clear"):
        st.session_state.root_pattern = ""
        st.session_state.candidate_root = ""
        st.rerun()

    if st.button("Generate Root", type="primary"):
        if not st.session_state.root_pattern:
            st.warning("Please add at least one C or V to the pattern.")
        else:
            st.session_state.candidate_root = generate_unique_root(st.session_state.root_pattern, consonants, vowels)

    if st.session_state.candidate_root:
        st.subheader("Generated Lemma")
        st.code(st.session_state.candidate_root, language="text")
        selected_lemma = st.session_state.candidate_root
else:
    manual_lemma = st.text_input(
        "Enter lemma",
        value=st.session_state.manual_lemma,
        help="Type a lemma directly instead of generating one from the syllable pattern.",
    ).strip()
    st.session_state.manual_lemma = manual_lemma

    if manual_lemma:
        st.subheader("Manual Lemma")
        st.code(manual_lemma, language="text")
        selected_lemma = manual_lemma

        if is_lemma_taken(manual_lemma):
            st.error(f"`{manual_lemma}` is already in `roots.json` or `compound_words.json`.")

if selected_lemma:
    if st.button("Accept Lemma"):
        if is_lemma_taken(selected_lemma):
            st.error(f"`{selected_lemma}` is already in `roots.json` or `compound_words.json`.")
        elif not gloss:
            st.success(f"Accepted lemma: {selected_lemma}")
            st.info("Add an English gloss to save it to `roots.json`.")
        else:
            roots = load_roots()
            roots[selected_lemma] = gloss
            save_roots(roots)
            st.session_state.root_pattern = ""
            st.session_state.candidate_root = ""
            st.session_state.manual_lemma = ""
            st.query_params["english"] = gloss
            st.switch_page("pages/dictionary.py")
