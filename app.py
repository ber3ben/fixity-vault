import streamlit as st
import pandas as pd
from audit_engine import run_full_audit

st.set_page_config(page_title="Fixity Vault", layout="wide")


def check_password():
    """Returns `True` if the user enters the correct password."""
    if st.session_state.get("password_correct", False):
        return True

    st.title("Fixity Vault - Authorized Access Only")
    st.caption("Please enter the portfolio access password to view the live app.")

    password_input = st.text_input("Password", type="password")

    if st.button("Log In"):
        # Retrieve password from st.secrets (defined in .streamlit/secrets.toml)
        if password_input == st.secrets.get("PORTFOLIO_PASSWORD", "demo123"):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


# Stop execution if password is wrong
if not check_password():
    st.stop()

# --- REST OF YOUR APP.PY UI CODE GOES HERE ---

# Custom Accessible Styling Injections
st.markdown("""
    <style>
    /* Force main app background */
    .stApp {
        background-color: #E6F4F1 !important;
    }
    
    /* Force sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #CFEADF !important;
    }

    /* Headings */
    h1, h2, h3 {
        color: #0B3C5D !important;
        font-weight: 700 !important;
    }

    /* Body Text & Captions */
    .stMarkdown, p, span, label, .stCaption {
        color: #0A192F !important;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #CFEADF !important;
        border: 2px solid #007A87 !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #005F6B !important;
        font-weight: bold !important;
    }

    /* Code Block Styling */
    div[data-testid="stCodeBlock"] {
        border: 2px solid #007A87 !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Fixity Vault")
st.caption("Standardized Internet Archive metadata for creative users, archivists, and researchers.")

@st.cache_data
def convert_df_to_csv(input_df: pd.DataFrame) -> bytes:
    """Converts a Pandas DataFrame into UTF-8 encoded CSV bytes."""
    return input_df.to_csv(index=False).encode('utf-8')

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("Query & Audit Settings")

target_collection = st.sidebar.text_input(
    "Internet Archive Collection",
    value="prelinger",
    help="Enter an Internet Archive collection identifier slug (e.g., prelinger, fedlink, computerchronicles)."
).strip().lower()

sample_limit = st.sidebar.slider(
    "Assets to Audit",
    min_value=5,
    max_value=50,
    value=15,
    step=5,
    key="sample_limit_slider"
)

st.sidebar.divider()
st.sidebar.header("Filter Results")

min_health = st.sidebar.slider(
    "Minimum Health Score (%)",
    min_value=0,
    max_value=100,
    value=0,
    step=5,
    key="min_health_slider"
)

search_query = st.sidebar.text_input(
    "Search Title or Creator",
    value="",
    placeholder="e.g. Prelinger, 1950, Design..."
)

# ---------------------------------------------------------
# DATA FETCHING
# ---------------------------------------------------------
with st.spinner(f"Fetching and auditing {sample_limit} items from '{target_collection}'..."):
    raw_df = run_full_audit(collection_name=target_collection, sample_size=sample_limit)

if raw_df.empty or "health_score" not in raw_df.columns:
    st.error("Unable to load audit data. Please check your network connection or Internet Archive API status.")
else:
    all_issues = set()
    for issue_str in raw_df["missing_issues"].dropna():
        if issue_str != "Clean Asset":
            all_issues.update([i.strip() for i in issue_str.split(",")])
    
    selected_issues = st.sidebar.multiselect(
        "Filter by Missing Metadata/Files",
        options=sorted(list(all_issues))
    )

    filtered_df = raw_df[raw_df["health_score"] >= min_health].copy()

    if search_query:
        query = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["title"].str.lower().str.contains(query, na=False) |
            filtered_df["creator"].str.lower().str.contains(query, na=False)
        ]

    if selected_issues:
        for issue in selected_issues:
            filtered_df = filtered_df[filtered_df["missing_issues"].str.contains(issue, na=False)]

    # ---------------------------------------------------------
    # METRICS ROW
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Displaying Assets", f"{len(filtered_df)} / {len(raw_df)}")
    avg_health = int(filtered_df['health_score'].mean()) if not filtered_df.empty else 0
    col2.metric("Average Collection Health", f"{avg_health}%")
    captions_count = len(filtered_df[filtered_df['has_captions'] == 'Yes']) if not filtered_df.empty else 0
    col3.metric("Assets with Captions", f"{captions_count} / {len(filtered_df)}")
    missing_licenses = len(filtered_df[filtered_df['license'] == 'MISSING']) if not filtered_df.empty else 0
    col4.metric("Assets Missing Licenses", missing_licenses)

    st.divider()

    # ---------------------------------------------------------
    # SPLIT SCREEN: INTERACTIVE TABLE & INSPECTOR
    # ---------------------------------------------------------
    table_col, inspector_col = st.columns([3, 2])

    with table_col:
        header_text_col, dl_button_col = st.columns([2, 1])
        with header_text_col:
            st.subheader("Collection Overview")
            st.caption("*Select row(s) to inspect media. Full audit data is included in the CSV export.*")
        with dl_button_col:
            csv_bytes = convert_df_to_csv(filtered_df)
            st.download_button(
                label="Export Full (CSV)",
                data=csv_bytes,
                file_name="archive_audit_report.csv",
                mime="text/csv",
                width="stretch"
            )

        ui_display_cols = [c for c in ["identifier", "has_thumbnail", "title"] if c in filtered_df.columns]

        selection_event = st.dataframe(
            filtered_df[ui_display_cols],
            column_config={
                "has_thumbnail": st.column_config.ImageColumn("Thumbnail"),
                "identifier": st.column_config.TextColumn("Identifier"),
                "title": st.column_config.TextColumn("Title")
            },
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row"
        )

    selected_row_indices = selection_event.selection.get("rows", [])
    
    if selected_row_indices and not filtered_df.empty:
        selected_assets = filtered_df.iloc[selected_row_indices]
    elif not filtered_df.empty:
        selected_assets = filtered_df.iloc[[0]]
    else:
        selected_assets = pd.DataFrame()

    # ---------------------------------------------------------
    # RIGHT SIDE INSPECTOR & BULK CREDIT GENERATOR
    # ---------------------------------------------------------
    with inspector_col:
        st.subheader("Media Inspector & Credits")
        
        if not selected_assets.empty:
            primary_asset = selected_assets.iloc[0]
            st.markdown(f"**Previewing:** `{primary_asset.get('identifier')}`")
            
            # Keep original case for URL request; inspect lower version strictly for extensions
            media_url = str(primary_asset.get("media_url", ""))
            media_url_lower = media_url.lower()
            
            AUDIO_EXTS = (".mp3", ".ogg", ".wav", ".aac", ".flac", ".m4a")
            VIDEO_EXTS = (".mp4", ".ogv", ".webm", ".mov")

            if media_url and media_url_lower != "none" and media_url_lower != "nan":
                if media_url_lower.endswith(AUDIO_EXTS):
                    st.audio(media_url)
                elif media_url_lower.endswith(VIDEO_EXTS):
                    st.video(media_url, format="video/mp4")
                else:
                    st.video(media_url)
            elif primary_asset.get("thumbnail_url"):
                st.image(primary_asset["thumbnail_url"], caption="Static Image Preview (No direct stream found)", width="stretch")
            else:
                st.warning("No direct web stream available for primary asset.")

            st.divider()

            # Generate Standardized Credit Blocks
            credit_blocks = []
            for _, asset in selected_assets.iterrows():
                block = f"""--- PUBLIC DOMAIN CREDIT BLOCK ---
Asset Title: {asset.get('title', 'N/A')} ({asset.get('date', 'N/A')})
Creator/Sponsor: {asset.get('creator', 'N/A')}
Source Identifier: archive.org/details/{asset.get('identifier', 'N/A')}
License Status: {asset.get('license', 'N/A')}
Web Stream: {asset.get('has_media', 'N/A')} | Captions: {asset.get('has_captions', 'N/A')}
Cataloged via Fixity Vault Engine
----------------------------------"""
                credit_blocks.append(block)

            full_credit_text = "\n\n".join(credit_blocks)

            credit_header_col, export_btn_col = st.columns([2, 1])
            with credit_header_col:
                st.markdown(f"**Public Domain Credits** ({len(selected_assets)} item(s))")
            with export_btn_col:
                st.download_button(
                    label="📄 Export Credits (.txt)",
                    data=full_credit_text,
                    file_name="public_domain_credits.txt",
                    mime="text/plain",
                    width="stretch"
                )

            st.code(full_credit_text, language="text")
        else:
            st.info("No asset selected or matching current filter criteria.")
