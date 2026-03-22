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


def normalize_simple_entry(left, right):
    if isinstance(right, dict):
        return None

    if not isinstance(left, str) or not isinstance(right, str):
        return None

    left_english = looks_like_english_gloss(left)
    right_english = looks_like_english_gloss(right)

    if left_english and not right_english:
        return {"English": left, "Conlang": right}
    if right_english and not left_english:
        return {"English": right, "Conlang": left}

    if len(left) <= len(right):
        return {"English": right, "Conlang": left}
    return {"English": left, "Conlang": right}


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


def normalize_root_entries(root, entry):
    if isinstance(entry, str):
        normalized = normalize_simple_entry(root, entry)
        if normalized:
            return [{"Type": "Base", "Root": root, **normalized, "Category": ""}]
        return []

    if not isinstance(entry, dict):
        return []

    rows = []
    forms = entry.get("forms", {})
    if isinstance(forms, dict):
        for form, form_entry in forms.items():
            if not isinstance(form, str) or not isinstance(form_entry, dict):
                continue
            meaning = form_entry.get("meaning", "")
            category = form_entry.get("category", "")
            if isinstance(meaning, list):
                meaning = ", ".join(meaning)
            if isinstance(meaning, str) and meaning:
                rows.append(
                    {
                        "Type": "Base",
                        "Root": root,
                        "English": meaning,
                        "Conlang": form,
                        "Category": category,
                    }
                )

    legacy_meaning = entry.get("meaning", "")
    if not rows and isinstance(legacy_meaning, str) and legacy_meaning:
        rows.append({"Type": "Base", "Root": root, "English": legacy_meaning, "Conlang": root, "Category": ""})

    return rows


st.title("Dictionary")
st.caption("Browse generated entries and compounds.")

st.markdown('''
## Design Rationale

### Function Words vs. Content Words
- The language **strictly separates function words and content words**, mainly due to phonological constraints.
- The phonotactic system allows only a limited set of **CV syllables**, which are reserved for **function words** (a closed class such as particles and grammatical markers).
- There are **40 possible CV syllables**, which is sufficient for the small inventory of grammatical items.
- A possible expansion is a **VCV pattern**, particularly for postpositions, which would provide **200 possible forms** for additional grammatical elements.

### Content Words
- **Content words** include **nouns, verbs, adjectives, and adverbs**.
- These are built from **CVC roots**, or compounds of such roots, followed by a **vowel suffix that marks word class**.
- The language allows **320 possible CVC roots**, creating a controlled but productive vocabulary base.

**Word class suffixes:**
- **Nouns:** `-a`  
- **Verbs:** `-u`  
- **Adjectives:** `-e`  
- **Adverbs:** `-o`

### Complementizers and Root Formation
- **Complementizers** were originally planned as derived forms but were reclassified as **function words**, since they belong to a closed grammatical class.
- Some lexical roots are created through **back-formation from function words**.  
  - Example: the root for “place” may derive from the function word “where” by adding a final consonant to form a valid **CVC root**.

### Expanded Vocabulary
- For less common concepts that cannot be expressed through compounding, the language allows **CVCVC roots**.
- There are approximately **12,800 possible CVCVC combinations**, providing enough space for additional vocabulary.
- Complex ideas can also be expressed through **multi-word constructions**.

## Word Formation Strategy

- The language relies heavily on **derivational morphology**.
- **Word class changes** are primarily handled through **suffixation**.
- **Lexical meaning** is often built through **compounding CVC roots**.

### Compounding Rules
- When two CVC roots combine, a **schwa is inserted** between them to avoid illegal consonant clusters.
- The exact phonotactic rules for compounding are still under development.
- To prevent overly long words, **compounds are limited to a maximum of three roots**.

### Deliberate Design Choices
The language intentionally avoids some strategies common in natural languages:

- **Opaque metaphorical extensions**  
  - Avoided because they rely on culture-specific knowledge and reduce transparency for learners.

- **Zero derivation (conversion)**  
  - Avoided because it creates ambiguity about a word’s syntactic category, making the language harder to learn and more difficult to parse computationally.
''')

if st.button("Refresh dictionary"):
    st.rerun()

roots = load_json("roots.json")
compounds = load_json("compound_words.json")
function_words = load_json("function_words.json")

if not roots and not compounds and not function_words:
    st.info("No dictionary data found. Go to the `Create Words` page first.")
    st.stop()

default_english_query = st.query_params.get("english", "")
english_query = st.text_input("English lookup", value=default_english_query).strip()
conlang_query = st.text_input("Conlang lookup").strip()
english_query_l = english_query.lower()
conlang_query_l = conlang_query.lower()

rows = []
if roots:
    for k, v in roots.items():
        rows.extend(normalize_root_entries(k, v))

if function_words:
    for k, v in function_words.items():
        normalized = normalize_simple_entry(k, v)
        if normalized:
            rows.append({"Type": "Function", "Root": "", **normalized, "Category": ""})

if compounds:
    for k, data in compounds.items():
        row = normalize_compound_entry(k, data)
        if row:
            rows.append({"Root": "", **row})

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
