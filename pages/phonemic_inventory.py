import pandas as pd
import streamlit as st

st.title("Phonemic Inventory")

st.header("Consonants")
phonemic_inventory = pd.DataFrame(
    {
        "Labial": ['p', 'm', '', ''], # columns
        "Alveolar": ['t', 'n', 's', 'l'],
        "Velar": ['k', '', '', ''],
        "Glottal": ['', '', 'h', '']
    },
    index=["Plosive", "Nasal", "Fricative", "Lateral approximant"], # rows
)
st.table(phonemic_inventory)

st.header("Vowels")
vowel_inventory = pd.DataFrame(
    {
        "Front": ['i', 'e', ''],
        "Central": ['', '', 'a'],
        "Back": ['u', 'o', '']
    },
    index=["Close", "Mid", "Open"],
)
st.table(vowel_inventory)

st.header("Syllable Structure and Phonotactic Constraints")
st.markdown('''
    Allowed syllables:
            
        V
        CV
        CVN (only with /n/ as the coda)
            
    Complex consonant clustered are not allowed, but there are six diphthongs composed from the three vowels with the maximal distance: /ai/, /ia/, /au/, /ua/, /ui/, and /iu/. Speakers can optionally inserts a glottal stop between the two vowels in a diphthong, transforming it into a sequence of V-V syllables.
''')

st.header("Phonological Processes")
st.markdown('''
    Additions and updates to the original rules:
    1. **Homorganic Nasal Assimilation**: It will only be applicable for compound words with the first root ending in /n/, since -n is mostly used as part of suffixes.
    
    2. **Vowel Harmony**: Vowels within a word may harmonize to share certain features. For instance, if a word contains a front vowel like /i/ or /e/, other vowels in the word may also become front vowels.
    
    3. **Glottalization**: In certain contexts, especially at the end of words, a glottal stop may be inserted after a vowel, particularly in diphthongs, resulting in a V-V syllable structure.
''')