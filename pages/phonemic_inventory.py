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

1. **Homorganic Nasal Assimilation**  
   Since nasals are allowed in codas, nasal consonants assimilate in place to a following consonant. This applies both word-internally and across word boundaries.
   
   _update_: It will only be applicable for compound words with the first root ending in /n/, since -n is mostly used as part of suffixes.
            
2. **Tone Spreading**  
   Tone may spread from one syllable to adjacent syllables within a phonological word, contributing to tonal coherence.

3. **Hiatus Resolution**  
   Because words may begin or end with vowels, vowel–vowel sequences can arise. Hiatus is resolved via glide insertion:
   - **[j]** is inserted after non-back vowels (/i, e/)
   - **[w]** is inserted after back vowels (/u, o, a/)

   Although **[j]** and **[w]** are not phonemes in the underlying inventory, they are typologically common and perceptually salient, making them suitable surface repair strategies.

   _update_: We are now allowing some diphthongs, so we will not resolve hiatuses in this way anymore.

4. **Resyllabification Within Words**  
   While **VC syllables** are not permitted phonotactically, they may arise in underlying representations if codas are used for grammatical purposes. In such cases, **VC.V sequences** are resyllabified as **V.CV** whenever possible.

5. **Vowel Epenthesis**  
   Adjacent identical nasals are separated by vowel epenthesis to preserve contrasts and avoid degemination. The epenthetic vowel copies the vowel of the preceding syllable.

   Example: `/ban.na/ → [ba.na.na]`  
   This maintains a clear distinction from `/ba.na/`.
            
   _update_: Now the epenthetic vowel between consonants will always be a schwa, as per feedback from last time.
''')