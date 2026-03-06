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