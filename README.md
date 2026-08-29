# fixity-vault

---


**Fixity Vault** is a lightweight, high-contrast Streamlit dashboard and audit engine designed to query, evaluate, and standardize metadata from the [Internet Archive](https://archive.org). Built for archivists, creative professionals, and researchers, it validates media assets, calculates collection health scores, and generates batch public domain attribution blocks.

---

## Features

* **Collection Auditing:** Query Internet Archive collection slugs (e.g., `prelinger`, `fedlink`, `computerchronicles`) with custom sample size controls.
* **Health Scoring & Issue Filtering:** Real-time collection metrics highlighting health scores, missing licenses, caption availability, and missing metadata.
* **Streamlined UI Table:** Clean interactive table displaying only essential visual indicators (`Identifier`, `Thumbnail`, `Title`).
* **Interactive Media Inspector:** Side-by-side inspector window that dynamically streams audio/video or displays image previews based on table selection.
* **Multi-Row Batch Credit Export:** Select single or multiple items to instantly generate, copy, or export standardized **Public Domain Credit Blocks** as plain text (`.txt`).
* **Complete Audit Export:** One-click CSV export containing the full dataset and all underlying metadata columns.
* **Accessible Light Palette:** High-contrast, non-neutral color scheme designed for readability and WCAG compliance.

---

## Project Structure

```text
fixity-vault/
├── app.py                     # Main Streamlit web application & interface
├── audit_engine.py            # Internet Archive API query & metadata processing engine
├── requirements.txt           # Python package dependencies
└── .streamlit/
    └── config.toml            # Global Streamlit theme & UI configurations

```

---

## Quickstart Guide

### 1. Prerequisites

Ensure you have **Python 3.9+** installed on your system.

### 2. Installation

Clone this repository and install the dependencies in your active Python environment:

```bash
git clone https://github.com/your-username/fixity-vault.git
cd fixity-vault

# Install or upgrade required dependencies
python -m pip install --upgrade "streamlit>=1.35.0" pandas requests

```

### 3. Launch the Dashboard

Always launch the app using `python -m streamlit run` to ensure Streamlit executes inside your target environment:

```bash
python -m streamlit run app.py

```

The application will launch automatically in your browser at `http://localhost:8501`.

---

## Theme & Accessibility Configuration

Fixity Vault uses a high-contrast palette (**Deep Teal**, **Light Seafoam**, **Crisp Mint**, and **Midnight Navy**) to avoid neutral grays/beiges while maintaining maximum legibility.

Custom theme parameters are managed in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#007A87"
backgroundColor = "#E6F4F1"
secondaryBackgroundColor = "#CFEADF"
textColor = "#0A192F"
font = "sans serif"

```

Additional component-level styling (e.g., metric card borders, code block containers, and background overrides) is handled via CSS injections near the top of `app.py`.

---

## License & Attribution

This tool processes publicly available metadata from the Internet Archive. Exported credit blocks are formatted for public domain attribution and archival recordkeeping.
