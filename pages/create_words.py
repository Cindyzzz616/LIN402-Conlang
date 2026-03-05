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


def save_roots(roots):
    with open("roots.json", "w", encoding="utf-8") as f:
        json.dump(roots, f, indent=2, ensure_ascii=False)


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


st.title("Create Words")

if "root_pattern" not in st.session_state:
    st.session_state.root_pattern = ""
if "candidate_root" not in st.session_state:
    st.session_state.candidate_root = ""

mode = st.radio("Choose what to create", ["Root", "Compound"], horizontal=True)

if mode == "Compound":
    st.info("Compound creation flow is ready for your next instructions.")
    st.stop()

inventory = load_inventory()
consonants = [p for p, v in inventory["phonemes"].items() if v["type"] == "consonant"]
vowels = [p for p, v in inventory["phonemes"].items() if v["type"] == "vowel"]

default_gloss = st.query_params.get("new_word", "")
gloss = st.text_input("English gloss (optional)", value=default_gloss).strip()

st.subheader("Syllable Structure")
st.text_input("Pattern", value=st.session_state.root_pattern, disabled=True)

c_col, v_col, back_col, clear_col = st.columns(4)
if c_col.button("C"):
    st.session_state.root_pattern += "C"
if v_col.button("V"):
    st.session_state.root_pattern += "V"
if back_col.button("Backspace"):
    st.session_state.root_pattern = st.session_state.root_pattern[:-1]
if clear_col.button("Clear"):
    st.session_state.root_pattern = ""
    st.session_state.candidate_root = ""

manual_pattern = st.text_input("Or type pattern manually (C and V only)", value=st.session_state.root_pattern)
clean_pattern = sanitize_pattern(manual_pattern)
if clean_pattern != st.session_state.root_pattern:
    st.session_state.root_pattern = clean_pattern

if st.button("Generate Root", type="primary"):
    if not st.session_state.root_pattern:
        st.warning("Please add at least one C or V to the pattern.")
    else:
        st.session_state.candidate_root = generate_root(st.session_state.root_pattern, consonants, vowels)

if st.session_state.candidate_root:
    st.subheader("Generated Lemma")
    st.code(st.session_state.candidate_root, language="text")

    regen_col, accept_col = st.columns(2)
    if regen_col.button("Generate New One"):
        st.session_state.candidate_root = generate_root(st.session_state.root_pattern, consonants, vowels)
    if accept_col.button("Accept Lemma"):
        if not gloss:
            st.success(f"Accepted lemma: {st.session_state.candidate_root}")
            st.info("Add an English gloss to save it to `roots.json`.")
        else:
            roots = load_roots()
            roots[gloss] = st.session_state.candidate_root
            save_roots(roots)
            st.success(f"Saved `{gloss}` -> `{st.session_state.candidate_root}` to roots.json")
