import streamlit as st
import json
import random
from itertools import product

# --- utility functions reused from existing scripts ---

def load_lexicon():
    words = []
    ignored = []
    with open("lexicon.json") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "=" in line:
                ignored.append(line)
            else:
                words.append(line)
    return words, ignored


def load_inventory():
    return json.load(open("phonemic_inventory.json"))


def make_syllable_pool():
    inv = load_inventory()
    consonants = [p for p, v in inv["phonemes"].items() if v["type"] == "consonant"]
    vowels = [p for p, v in inv["phonemes"].items() if v["type"] == "vowel"]
    syllables = [o + n + c for o, n, c in product(consonants, vowels, consonants)]
    random.shuffle(syllables)
    return syllables, consonants, vowels


def assign_groups(words, syllables, consonants):
    mapping = {}
    remaining = set(words)
    groups = [
        ["black", "white", "red", "yellow", "grue"],
        ["good", "bad"],
        ["old", "young/new"],
        ["cold", "warm", "hot"],
        ["wet", "dry"],
        ["big", "small"],
        ["thick", "thin"],
        ["long/tall", "short"],
        ["sharp", "dull"],
        ["light (weight)", "heavy"],
        ["rotten", "fresh"],
        ["male", "female"],
        ["night", "day"],
        ["live", "die"],
        ["push", "pull"],
        ["first person singular", "second person singular", "third person singular"],
        ["this (determiner)", "that (determiner)"]
    ]

    def pop_syl(pred):
        for i, s in enumerate(syllables):
            if pred(s):
                return syllables.pop(i)
        return None

    for grp in groups:
        present = [w for w in grp if w in remaining]
        if not present:
            continue
        if len(present) > 2:
            c = random.choice(consonants)
            for w in present:
                syl = pop_syl(lambda s: s.startswith(c))
                if syl is None:
                    syl = pop_syl(lambda s: True)
                mapping[w] = syl
                remaining.remove(w)
        else:
            if len(present) == 1:
                w = present[0]
                mapping[w] = pop_syl(lambda s: True)
                remaining.remove(w)
            else:
                w1, w2 = present
                syl1 = pop_syl(lambda s: True)
                if syl1 is None:
                    continue
                cv = syl1[:2]
                syl2 = pop_syl(lambda s: s.startswith(cv))
                if syl2 is None:
                    syl2 = pop_syl(lambda s: True)
                mapping[w1] = syl1
                mapping[w2] = syl2
                remaining.remove(w1)
                remaining.remove(w2)

    # remaining
    for w in list(remaining):
        syl = pop_syl(lambda s: True)
        if syl is None:
            break
        mapping[w] = syl
        remaining.remove(w)

    return mapping, remaining


def save_mapping(mapping, ignored):
    with open("lexicon_mapped.json", "w") as f:
        json.dump(mapping, f, indent=2)
    with open("lexicon_ignored.txt", "w") as f:
        f.write("\n".join(ignored))


def main():
    st.title("Conlang Lexicon Mapper")

    words, ignored = load_lexicon()
    st.sidebar.header("Input data")
    st.sidebar.write(f"{len(words)} words, {len(ignored)} ignored lines")

    if st.sidebar.button("Generate mapping"):
        syllables, consonants, vowels = make_syllable_pool()
        mapping, remaining = assign_groups(words, syllables, consonants)
        save_mapping(mapping, ignored)
        st.success(f"Generated {len(mapping)} entries; {len(remaining)} unassigned")
        st.write(mapping)

    if st.sidebar.button("Show mapping (file)"):
        try:
            with open("lexicon_mapped.json") as f:
                data = json.load(f)
            st.write(data)
        except FileNotFoundError:
            st.error("No mapping file yet; generate one first.")

    if st.sidebar.button("Create compounds"):
        # reuse code from make_compounds
        rules = json.load(open("derivation_rules.json"))
        roots = json.load(open("roots.json"))
        compound = {}
        for line in ignored:
            if not line or "=" not in line:
                continue
            left, right = line.split("=", 1)
            left = left.strip()
            parts = [p.strip() for p in right.split("+") if p.strip()]
            lemma_roots = []
            suffix = ""
            used_roots = {}
            for p in parts:
                if p.startswith("-"):
                    key = p[1:]
                    if key == "adj":
                        key = "adjective"
                    if key == "noun":
                        key = "noun"
                    if key == "verb":
                        key = "verb"
                    if key == "complementizer":
                        key = "complementizer"
                    if key in rules:
                        suffix = rules[key]["suffix"]
                else:
                    term = p
                    if term in roots:
                        val = roots[term]
                        lemma_roots.append(val)
                        used_roots[term] = val
                    else:
                        found = None
                        for rk in roots:
                            if term in rk:
                                found = rk
                                break
                        if found:
                            val = roots[found]
                            lemma_roots.append(val)
                            used_roots[found] = val
                        else:
                            st.warning(f"missing root for {term}")
            lemma = "-".join(lemma_roots) + suffix
            compound[left] = {"lemma": lemma, "roots": used_roots}
        with open("compound_words.json", "w") as out:
            json.dump(compound, out, indent=2)
        st.success(f"Written {len(compound)} compounds")
        st.write(compound)

if __name__ == "__main__":
    main()
