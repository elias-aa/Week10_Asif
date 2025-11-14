# Setup and run

This project uses a local virtual environment to isolate dependencies.

Quick steps to create and activate the environment, then run the Streamlit app:

1. Create the virtual environment and install packages (one-liner):

```bash
bash setup_venv.sh
```

2. Activate the environment:

```bash
source .venv/bin/activate
```

3. Run the Streamlit app:

```bash
streamlit run elias_week10.py
```

Notes:
- The app expects `cloudmart_multi_account.csv` in the repository root. Place the CSV there before running.
- If you prefer a different venv location, modify `setup_venv.sh` accordingly.
