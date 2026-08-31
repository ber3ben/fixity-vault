# README

**Fixity Vault** is a lightweight, high-contrast Streamlit dashboard and audit engine designed to query, evaluate, and standardize metadata from the [Internet Archive](https://archive.org). Built for archivists, creative professionals, and researchers, it validates media assets, calculates collection health scores, and generates batch public domain attribution blocks.

---

## Features

* **Collection Auditing:** Query Internet Archive collection slugs (e.g., `prelinger`, `fedlink`, `computerchronicles`) with custom sample size controls.
* **Health Scoring & Issue Filtering:** Real-time collection metrics highlighting health scores, missing licenses, caption availability, and missing metadata.
* **Streamlined UI Table:** Clean interactive table displaying only essential visual indicators (`Identifier`, `Thumbnail`, `Title`).
* **Interactive Media Inspector:** Side-by-side inspector window that dynamically streams audio/video or displays image previews based on table selection.
* **Multi-Row Batch Credit Export:** Select single or multiple items to instantly generate, copy, or export standardized **Public Domain Credit Blocks** as plain text (`.txt`).
* **Complete Audit Export:** One-click CSV export containing the full dataset and all underlying metadata columns.
* **Optional Authentication Layer:** Features built-in, lightweight password protection via Streamlit session state and local secrets management.
* **Accessible Light Palette:** High-contrast, non-neutral color scheme designed for readability and WCAG compliance.

---

## Tech Stack

* **UI & Dashboard:** [Streamlit](https://streamlit.io/) (Custom CSS with high-contrast accessible styling)
* **Data Processing & Analytics:** [Pandas](https://pandas.pydata.org/)
* **Schema Validation & Data Integrity:** [Pydantic v2](https://docs.pydantic.dev/)
* **API Communications:** `requests` / Internet Archive Advanced Search & Metadata API
  
---
## Project Structure

```text
fixity-vault/
├── .streamlit/
│   └── secrets.toml        # Local secrets (password auth, ignored by Git)
├── app.py                  # Main Streamlit dashboard UI & authentication
├── audit_engine.py         # Data fetching, metric calculations, & pipeline processing
├── schema.py               # Pydantic v2 schemas and validation logic
├── test_pipeline.py        # Local verification and integration test suite
├── requirements.txt        # Core project dependencies
└── README.md               # Project documentation

```

---

## Local Quickstart Guide

### 1. Prerequisites

Ensure you have Python installed on your system.

### 2. Clone the Repository

```bash
git clone [https://github.com/your-username/fixity-vault.git](https://github.com/your-username/fixity-vault.git)
cd fixity-vault

```

### 3. Create & Activate a Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

```

### 4. Install Dependencies

```bash
pip install -r requirements.txt

```

### 5. Run the Local Test Suite

Verify that all schema validators, engine endpoints, and conversion utilities work before launching the UI:

```bash
python test_pipeline.py

```

### 6. Launch the Application

```bash
streamlit run app.py

```

Navigating to `http://localhost:8501` in your web browser will open the app.

---
### Environment & Secrets Setup

1. Create a `.streamlit` folder in the root directory.
2. Add a `secrets.toml` file inside `.streamlit/` with your local access password:
   ```toml
   PORTFOLIO_PASSWORD = "your_custom_password"
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

Distributed under the MIT License. See `LICENSE` for more information.

This tool processes publicly available metadata from the Internet Archive. Exported credit blocks are formatted for public domain attribution.

### I do not work for or are professionally affiliated with the Internet Archive.
