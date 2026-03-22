import json
import random

import streamlit as st


NOUN_CLASS_PREFIXES = {
    "Class I: Humans, community, kinship": "m",
    "Class II: Technology, tools, manmade artifacts": "k",
    "Class III: Locations, places": "p",
    "Class IV: Plants, animals, edible things, organic things": "n",
    "Class VI: Actions/activities": "l",
    "Class V: Inorganic things found in nature; substances": "t",
    "Class VII: Time, events": "s",
    "Class VIII: Abstract concepts, intangible things, emotions": "h"
}

WORD_CLASS_SUFFIXES = {
    "a": "noun",
    "o": "adverb",
    "u": "verb",
    "e": "adjective",
}


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


def build_root_entry(root, forms):
    return {"forms": forms}


def is_lemma_taken(lemma):
    """Check if a lemma is already used in roots.json or compound_words.json"""
    roots = load_roots()
    compounds = load_compounds()

    for root, entry in roots.items():
        if root == lemma:
            return True
        if isinstance(entry, str) and entry == lemma:
            return True
        if isinstance(entry, dict):
            if entry.get("meaning") == lemma:
                return True
            forms = entry.get("forms", {})
            if isinstance(forms, dict) and lemma in forms:
                return True

    for compound_lemma, entry in compounds.items():
        if compound_lemma == lemma:
            return True
        if entry.get("lemma") == lemma:
            return True

    return False


def sanitize_pattern(pattern):
    return "".join(ch for ch in pattern.upper() if ch in {"C", "V"})


def first_consonant(text, consonants):
    consonant_set = set(consonants)
    for char in text:
        if char in consonant_set:
            return char
    return ""


def matches_noun_class_prefix(lemma, required_prefix, consonants):
    if not required_prefix:
        return True
    return first_consonant(lemma, consonants) == required_prefix


def generate_root(pattern, consonants, vowels, required_prefix=None):
    generated = []
    used_required_prefix = False
    for symbol in pattern:
        if symbol == "C":
            if required_prefix and not used_required_prefix:
                generated.append(required_prefix)
                used_required_prefix = True
            else:
                generated.append(random.choice(consonants))
        elif symbol == "V":
            generated.append(random.choice(vowels))
    return "".join(generated)


def generate_unique_root(pattern, consonants, vowels, required_prefix=None, max_attempts=100):
    """Generate a root that is not already taken in roots.json or compound_words.json"""
    for _ in range(max_attempts):
        candidate = generate_root(pattern, consonants, vowels, required_prefix=required_prefix)
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
if "saved_lemma" not in st.session_state:
    st.session_state.saved_lemma = ""
if "saved_forms" not in st.session_state:
    st.session_state.saved_forms = []

mode = st.radio("Choose what to create", ["Root", "Compound"], horizontal=True)

if mode == "Compound":
    st.info("Compound creation flow is ready for your next instructions.")
    st.stop()

inventory = load_inventory()
consonants = [p for p, v in inventory["phonemes"].items() if v["type"] == "consonant"]
vowels = [p for p, v in inventory["phonemes"].items() if v["type"] == "vowel"]

default_gloss = st.query_params.get("new_word", "")

if st.session_state.saved_lemma:
    saved_forms = ", ".join(st.session_state.saved_forms)
    st.success(
        f"Saved `{st.session_state.saved_lemma}` to `roots.json`"
        f" with forms: {saved_forms}."
    )
    st.session_state.saved_lemma = ""
    st.session_state.saved_forms = []

selected_noun_class = st.selectbox(
    "Noun class",
    options=list(NOUN_CLASS_PREFIXES.keys()),
)
required_prefix = NOUN_CLASS_PREFIXES[selected_noun_class]
st.caption(f"Words in this class must use `{required_prefix}` as their first consonant.")

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
        elif "C" not in st.session_state.root_pattern:
            st.warning("The pattern must include at least one C so the noun class prefix can be applied.")
        else:
            st.session_state.candidate_root = generate_unique_root(
                st.session_state.root_pattern,
                consonants,
                vowels,
                required_prefix=required_prefix,
            )

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
        if not matches_noun_class_prefix(manual_lemma, required_prefix, consonants):
            st.error(
                f"`{manual_lemma}` does not match the selected noun class. "
                f"Its first consonant must be `{required_prefix}`."
            )
        else:
            selected_lemma = manual_lemma

        if is_lemma_taken(manual_lemma):
            st.error(f"`{manual_lemma}` is already in `roots.json` or `compound_words.json`.")

if selected_lemma:
    st.subheader("Derived Forms")
    form_config = {}
    for suffix, category in WORD_CLASS_SUFFIXES.items():
        form = f"{selected_lemma}{suffix}"
        include_default = suffix == "a"
        meaning_default = default_gloss if suffix == "a" else ""
        include = st.checkbox(
            f"Keep {category}: `{form}`",
            value=include_default,
            key=f"{selected_lemma}_{suffix}_include",
        )
        meaning = st.text_input(
            f"{category.capitalize()} meaning",
            value=meaning_default,
            key=f"{selected_lemma}_{suffix}_meaning",
        ).strip()
        form_config[suffix] = {
            "form": form,
            "category": category,
            "include": include,
            "meaning": meaning,
        }

    if st.button("Accept Lemma"):
        if is_lemma_taken(selected_lemma):
            st.error(f"`{selected_lemma}` is already in `roots.json` or `compound_words.json`.")
        elif not matches_noun_class_prefix(selected_lemma, required_prefix, consonants):
            st.error(
                f"`{selected_lemma}` does not match the selected noun class. "
                f"Its first consonant must be `{required_prefix}`."
            )
        else:
            kept_forms = {
                config["form"]: {
                    "category": config["category"],
                    "meaning": config["meaning"],
                }
                for config in form_config.values()
                if config["include"]
            }
            if not kept_forms:
                st.error("Keep at least one derived form before saving this root.")
            else:
                missing_meanings = [config["form"] for config in form_config.values() if config["include"] and not config["meaning"]]
                if missing_meanings:
                    st.error("Add an English meaning for each kept form: " + ", ".join(missing_meanings))
                else:
                    roots = load_roots()
                    roots[selected_lemma] = build_root_entry(selected_lemma, kept_forms)
                    save_roots(roots)
                    st.session_state.saved_lemma = selected_lemma
                    st.session_state.saved_forms = list(kept_forms.keys())
                    st.session_state.candidate_root = ""
                    st.session_state.manual_lemma = ""
                    st.query_params["new_word"] = default_gloss
                    st.rerun()
