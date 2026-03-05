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
