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
    st.title("LIN402 Conlang (Name TBD)")
    st.markdown(body='''

    This constructed language is designed as an international auxiliary language optimized for both human communication and computational processing. Its structure reflects a deliberate attempt to balance learnability, typological naturalness, and machine interpretability. The language is intended to function as a neutral pivot language in multilingual environments and as an intermediate representation for natural language processing systems.

    The design is strongly influenced by the needs of the Mora project, a language learning platform that processes user-generated videos and must analyze, translate, and evaluate linguistic content across many languages. By providing a standardized linguistic structure that is easy for both humans and machines to parse, the language aims to facilitate translation, transcription, and language learning across diverse linguistic backgrounds.

    ---

    # Typological Profile

    The language adopts a strictly head-final typological orientation. Its basic word order is **SOV (subject–object–verb)**, and grammatical relations are primarily expressed through suffixation and word order.

    Head-final design ensures structural consistency across the grammar: modifiers precede heads, subordinate clauses precede main clauses, and grammatical marking is largely suffixing. This typological alignment improves both human learnability and computational parsing.

    ---

    # Phonology

    The phonological system is intentionally minimal and acoustically distinct. The inventory prioritizes phonemes that are widely attested across languages and avoids contrasts that are difficult for learners or unreliable for speech recognition systems.

    ## Consonants

    The consonant inventory consists of a small set of highly frequent phonemes:

    p, t, k  
    m, n  
    s, h  
    l  

    Voiced plosives and rhotics are excluded to reduce perceptual confusion and cross-linguistic variability.

    ## Vowels

    The vowel system consists of five vowels:

    i, e, a, o, u

    Five-vowel systems are among the most common cross-linguistically and provide maximal acoustic spacing while maintaining simplicity. Each vowel may also carry high or low tone, increasing the number of possible lexical contrasts without expanding the segment inventory.

    ## Syllable Structure

    The permitted syllable types are:

    - V  
    - CV  
    - CVN  

    Only **/n/** may appear in coda position, and complex codas are not permitted. These constraints simplify syllable parsing for both human learners and computational systems.

    Several phonological repair processes maintain these restrictions, including nasal assimilation, glide insertion for hiatus resolution, and vowel epenthesis.

    ---

    # Lexicon

    The lexicon is primarily **a priori**, meaning that most words are not directly derived from existing natural languages. However, certain phonological patterns reflect widely attested sound-symbolic tendencies, such as nasal sounds in negation markers.

    Synonymy is deliberately limited. Semantic contrasts are often expressed through minimal phonological differences, allowing systematic relationships between related lexical items.

    The language also allows optional semantic distinctions, especially in kinship terminology. Speakers may optionally encode distinctions such as gender or age (e.g., older vs. younger siblings), but these distinctions are not grammatically required.

    Another central design principle is **semantic underspecification**. Lexical items often carry broad meanings that can be refined through additional morphemes or function words. This allows complexity to be introduced incrementally rather than encoded directly into lexical items.

    ---

    # Morphology

    The language uses a strictly **suffixing morphological system**, consistent with its head-final syntax.

    A notable feature is the absence of inherent lexical categories. Words are not intrinsically nouns, verbs, or adjectives; instead, their grammatical role is determined by syntactic position or by optional suffixes.

    Derivational morphology assigns grammatical categories using vowel suffixes:

    - **-a** → noun  
    - **-i** → adjective  
    - **-u** → verb  
    - **-e** → complementizer  
    - **-o** → adverb  

    Certain inflectional morphemes appear as diphthongs:

    - **-ai** → possessive  
    - **-ui** → imperative  

    These suffixes introduce grammatical distinctions while preserving a highly regular morphological structure.

    ---

    # Syntax

    Syntax is governed primarily by fixed word order and regular structural patterns. The dominant clause type follows **SOV order**, with modifiers preceding the elements they modify.

    The language supports several clause types, including:

    - declarative clauses  
    - interrogative clauses  
    - imperative clauses  
    - conditional clauses  
    - causal clauses  

    Coordination and subordination are expressed through function words and complementizers. Arguments may be omitted when their referents are recoverable from context.

    Although clause embedding is possible, excessive nesting is discouraged in order to preserve structural clarity and ease of processing.

    ---

    # Design Philosophy

    This language can be viewed as part of the tradition of **philosophical languages**, which attempt to rationalize or optimize linguistic systems. However, unlike earlier philosophical languages that aimed to eliminate ambiguity entirely, this language embraces controlled polysemy and underspecification.

    Lexical meanings are intentionally broad, with additional morphemes functioning as operators that refine interpretation. This modular approach allows the language to remain simple at its core while still supporting expressive and precise communication.

    ---

    # Summary

    Overall, this conlang is a minimalist, head-final auxiliary language designed to function as both a human lingua franca and a computational intermediary. Its small phoneme inventory, regular morphology, flexible word classes, and consistent syntax aim to maximize learnability and machine readability while remaining typologically plausible.

    By combining insights from linguistic typology, second language acquisition, and natural language processing, the language attempts to bridge the gap between human communication and computational language systems.'''
    )

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
