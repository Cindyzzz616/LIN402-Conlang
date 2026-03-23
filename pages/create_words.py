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


def load_json_file(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def load_inventory():
    with open("phonemic_inventory.json", encoding="utf-8") as f:
        return json.load(f)


def load_roots():
    return load_json_file("roots.json", {})


def load_compounds():
    return load_json_file("compound_words.json", {})


def load_derivation_rules():
    return load_json_file("derivation_rules.json", {})


def save_roots(roots):
    with open("roots.json", "w", encoding="utf-8") as f:
        json.dump(roots, f, indent=2, ensure_ascii=False)


def save_compounds(compounds):
    with open("compound_words.json", "w", encoding="utf-8") as f:
        json.dump(compounds, f, indent=2, ensure_ascii=False)


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


def normalize_rule_category(rule_name):
    if rule_name.endswith(" noun"):
        return "noun"
    return rule_name


def build_base_lookup_entries(roots):
    entries = []
    for root, entry in roots.items():
        if not isinstance(root, str):
            continue

        forms = entry.get("forms", {}) if isinstance(entry, dict) else {}
        if isinstance(forms, dict) and forms:
            meanings = []
            categories = []
            for form_entry in forms.values():
                if not isinstance(form_entry, dict):
                    continue
                meaning = form_entry.get("meaning", "")
                if isinstance(meaning, list):
                    meaning = ", ".join(meaning)
                category = form_entry.get("category", "")
                if isinstance(meaning, str) and meaning:
                    meanings.append(meaning)
                if isinstance(category, str) and category:
                    categories.append(category)

            unique_meanings = ", ".join(dict.fromkeys(meanings))
            unique_categories = ", ".join(dict.fromkeys(categories)) or "uncategorized"
            if unique_meanings:
                entries.append(
                    {
                        "root": root,
                        "meaning": unique_meanings,
                        "category": unique_categories,
                        "label": f"{root} ({unique_categories}) -> {unique_meanings}",
                    }
                )
        elif isinstance(entry, dict):
            meaning = entry.get("meaning", "")
            if isinstance(meaning, list):
                meaning = ", ".join(meaning)
            if isinstance(meaning, str) and meaning:
                entries.append(
                    {
                        "root": root,
                        "meaning": meaning,
                        "category": "",
                        "label": f"{root} -> {meaning}",
                    }
                )
    return entries


def resolve_compound_component(slot_name, lookup_entries):
    mode = st.radio(
        f"{slot_name} source",
        ["Lookup dictionary", "Enter manually"],
        horizontal=True,
        key=f"{slot_name}_source_mode",
    )

    if mode == "Lookup dictionary":
        english_query = st.text_input(
            f"{slot_name} English lookup",
            key=f"{slot_name}_english_lookup_query",
            help="Search by English meaning.",
        ).strip().lower()
        conlang_query = st.text_input(
            f"{slot_name} Conlang lookup",
            key=f"{slot_name}_conlang_lookup_query",
            help="Search by the base root in the conlang.",
        ).strip().lower()
        filtered_entries = [
            entry
            for entry in lookup_entries
            if (not english_query or english_query in entry["meaning"].lower())
            and (not conlang_query or conlang_query in entry["root"].lower())
        ]
        if not filtered_entries:
            st.warning(f"No base words matched the {slot_name.lower()} lookup.")
            return None

        selected_label = st.selectbox(
            f"{slot_name} base word",
            options=[entry["label"] for entry in filtered_entries],
            key=f"{slot_name}_lookup_choice",
        )
        selected_entry = next(entry for entry in filtered_entries if entry["label"] == selected_label)
        st.caption(f"{slot_name}: using root `{selected_entry['root']}` with meaning `{selected_entry['meaning']}`.")
        return {"root": selected_entry["root"], "meaning": selected_entry["meaning"]}

    manual_root = st.text_input(
        f"{slot_name} root",
        key=f"{slot_name}_manual_root",
        help="Enter the base root directly.",
    ).strip()
    manual_meaning = st.text_input(
        f"{slot_name} meaning",
        key=f"{slot_name}_manual_meaning",
        help="English gloss for this base root.",
    ).strip()
    if manual_root:
        st.caption(f"{slot_name}: manual root `{manual_root}`.")
    if manual_root and manual_meaning:
        return {"root": manual_root, "meaning": manual_meaning}
    return None


def build_compound_lemma(first_root, second_root, suffix, consonants):
    clean_suffix = suffix.lstrip("-")
    if not first_root or not second_root:
        return ""

    left_ends_consonant = first_root[-1] in consonants
    right_starts_consonant = second_root[0] in consonants
    joiner = "'" if left_ends_consonant and right_starts_consonant else ""
    return f"{first_root}{joiner}{second_root}{clean_suffix}"


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
if "saved_target_file" not in st.session_state:
    st.session_state.saved_target_file = ""

mode = st.radio("Choose what to create", ["Root", "Compound"], horizontal=True)

inventory = load_inventory()
consonants = [p for p, v in inventory["phonemes"].items() if v["type"] == "consonant"]
vowels = [p for p, v in inventory["phonemes"].items() if v["type"] == "vowel"]
roots = load_roots()
derivation_rules = load_derivation_rules()

default_gloss = st.query_params.get("new_word", "")

if st.session_state.saved_lemma:
    saved_forms = ", ".join(st.session_state.saved_forms)
    st.success(
        f"Saved `{st.session_state.saved_lemma}` to `{st.session_state.saved_target_file or 'roots.json'}`"
        f" with forms: {saved_forms}."
    )
    st.session_state.saved_lemma = ""
    st.session_state.saved_forms = []
    st.session_state.saved_target_file = ""

if mode == "Compound":
    st.subheader("Compound Builder")
    st.caption("Choose two base roots from the dictionary or enter them manually, then pick the category and suffix.")

    lookup_entries = build_base_lookup_entries(roots)
    left_col, right_col = st.columns(2)
    with left_col:
        first_component = resolve_compound_component("First word", lookup_entries)
    with right_col:
        second_component = resolve_compound_component("Second word", lookup_entries)

    compound_meaning = st.text_input(
        "Compound meaning",
        value=default_gloss,
        help="English gloss for the finished compound.",
    ).strip()

    available_categories = sorted({normalize_rule_category(name) for name in derivation_rules}) or ["noun"]
    syntactic_category = st.selectbox("Syntactic category", available_categories)

    suffix_options = []
    for rule_name, rule_config in derivation_rules.items():
        suffix = rule_config.get("suffix", "")
        if not suffix:
            continue
        normalized_category = normalize_rule_category(rule_name)
        label = f"{rule_name} ({suffix})"
        suffix_options.append(
            {
                "label": label,
                "rule_name": rule_name,
                "suffix": suffix,
                "category": normalized_category,
            }
        )

    matching_suffix_options = [option for option in suffix_options if option["category"] == syntactic_category]
    if not matching_suffix_options:
        st.error(f"No suffixes in derivation_rules.json match the category `{syntactic_category}`.")
        st.stop()

    selected_suffix_label = st.selectbox(
        "Suffix from derivation rules",
        options=[option["label"] for option in matching_suffix_options],
    )
    selected_suffix = next(option for option in matching_suffix_options if option["label"] == selected_suffix_label)

    first_root = first_component["root"] if first_component else ""
    second_root = second_component["root"] if second_component else ""
    compound_lemma = build_compound_lemma(first_root, second_root, selected_suffix["suffix"], consonants)

    st.subheader("Compound Preview")
    st.code(compound_lemma or "(choose both base words to preview the compound)", language="text")
    if first_root and second_root and first_root[-1] in consonants and second_root[0] in consonants:
        st.caption("Inserted `'` between the two roots because the boundary would otherwise create a consonant cluster.")

    if st.button("Save Compound", type="primary"):
        if not first_component or not second_component:
            st.error("Choose or enter both base words before saving the compound.")
        elif not compound_meaning:
            st.error("Add an English meaning for the compound.")
        elif not compound_lemma:
            st.error("The compound lemma could not be generated.")
        elif is_lemma_taken(compound_lemma):
            st.error(f"`{compound_lemma}` is already in `roots.json` or `compound_words.json`.")
        else:
            compounds = load_compounds()
            compounds[compound_lemma] = {
                "roots": {
                    first_component["root"]: first_component["meaning"],
                    second_component["root"]: second_component["meaning"],
                },
                "meaning": compound_meaning,
                "syntactic_category": syntactic_category,
            }
            save_compounds(compounds)
            st.session_state.saved_lemma = compound_lemma
            st.session_state.saved_forms = [selected_suffix["rule_name"]]
            st.session_state.saved_target_file = "compound_words.json"
            st.query_params["new_word"] = compound_meaning
            st.rerun()

    st.stop()

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
                    st.session_state.saved_target_file = "roots.json"
                    st.session_state.candidate_root = ""
                    st.session_state.manual_lemma = ""
                    st.query_params["new_word"] = default_gloss
                    st.rerun()
