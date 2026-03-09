# LIN402-Conlang

A simple conlang lexicon generator that assigns syllables to words and builds compound lemmas.

## Streamlit App

A lightweight web interface is provided via Streamlit. Because the system Python is managed by Homebrew, it's easiest to run the app inside a virtual environment.

1. **Create and activate a virtual environment** (from the project root):

    ```bash
    python3 -m venv .venv          # or another path
    source .venv/bin/activate      # macOS / Linux
    # (on Windows use `.venv\\Scripts\\activate`)
    ```

2. **Install the dependencies**:

    ```bash
    pip install --upgrade pip
    pip install streamlit
    ```

3. **Select the `.venv` interpreter** in VS Code so Pylance can resolve imports (Command Palette ➜ "Python: Select Interpreter").

4. **Run the application**:

    ```bash
    streamlit run streamlit_app.py
    ```

The sidebar exposes buttons for generating mappings, viewing existing results, and creating compounds.

> ⚠️ If you choose not to use a virtual environment, you may need to install with `pipx` or pass
> `--break-system-packages` to `pip` as described by Homebrew, but a venv is strongly recommended.

## TODO

- [ ] Figure out allophones for each phoneme - would cover the entire IPA

## Scratchpad

- 40 CV syllables, 320 CVC syllables

Content words

- Noun (Naming word): Person, place, thing, or idea (e.g., cat, teacher, love, London).
    - suffix -a
- Pronoun (Replacement): Replaces a noun to avoid repetition (e.g., she, it, they, this).
- Verb (Action/State): Describes what the subject does or its state of being (e.g., run, is, think, seem).
    - suffix -u
- Adjective (Modifier): Describes or modifies a noun or pronoun (e.g., happy, fast, blue, intelligent).
    - suffix -e
- Adverb (Modifier): Modifies a verb, adjective, or other adverb; often indicates how, when, or where (e.g., quickly, yesterday, here, very).
    - suffix -o

Function words

- articles — the and a. In some inflected languages, the articles may take on the case of the declension of the following noun.
    - this
    - that

- pronouns — he/him, she/her, etc. — inflected in English
    - 3

- adpositions — in, under, towards, before, of, for, etc.


- co-ordinating conjunctions — and, or, but, etc.
    - 5
    - and
    - or
    - but
    - because
    - therefore


- subordinating conjunctions — if, than, however, thus, etc.
    - if
    - than
    - however
    - not

- auxiliary verbs — would, could, should, etc. — inflected in English

- particles — up, on, down, out, etc.

- interjections — oh, ah, eh, etc. — sometimes called "filled pauses"
    - won't specify this

- expletives — indeed, friggin’, zounds, etc.
    - these will be longer words

- sentence words — yes, no, okay, etc.
    - yes
    - no
    - ok



- Complementizer

- Postposition (Connector): Links a noun/pronoun to another word, often indicating time, place, or direction (e.g., in, on, at, through).

- Conjunction (Linker): Connects words, phrases, or clauses (e.g., and, but, or, because).
- Interjection (Emotion): An exclamation expressing sudden emotion (e.g., Wow, Ouch, Hey). 



	Phone
	Tablet
	Scroll
	Like
	Comment
	Share
	Follow
	Message
	Record
	Take picture
	Upload
	Download
	Internet
	Technology
	Connection
	Screen
	Photo
	Video
	Audio
	Bluetooth 

	Practice
	Learn
	Reading
	Listening
	Writing
	Speaking
	Grammar
	Phonology
	Morphology
	Syntax
	Semantics
	Review
	Notice
	Natural 
	Interact
	Error
	Correct
	Spelling
	Word
	Sentence 
	Teach 
	Type



	Culture
	Language
	Country
	Province/state
	City
	World
	Continent
	Cuisine
	Travel
	Ethnicity
	Race
	Name
	Gender
	Welcome
	Passport
	Visa
	Citizenship
	Immigration
	Work
	School
