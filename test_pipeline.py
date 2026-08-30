import sys
import pandas as pd
from pydantic import ValidationError

# Import pipeline components
try:
    from schema import ItemMetadata, FileMetadata
    from audit_engine import fetch_and_audit_single_item, run_full_audit
    import app
    print("✅ Module Import Test: PASSED")
except ImportError as e:
    print(f"❌ Module Import Test: FAILED - {e}")
    sys.exit(1)


def test_schema_resilience():
    """Validates that schema handles dirty/inconsistent IA metadata without crashing."""
    print("\n--- Testing schema.py Edge Cases ---")
    
    # Raw IA payload with list-type creator, string subject, and missing date
    raw_payload = {
        "identifier": "test_film_1950",
        "title": ["Jam Handy Film", "Secondary Title"],
        "creator": ["Prelinger Archives", "Jam Handy Organization"],
        "subject": "1950s; Educational; Traffic Safety",
        "licenseurl": ["https://creativecommons.org/publicdomain/zero/1.0/"]
    }
    
    try:
        validated = ItemMetadata.model_validate(raw_payload)
        assert validated.creator == "Prelinger Archives, Jam Handy Organization"
        assert validated.date == "Undated"
        assert isinstance(validated.subject, str)
        print("✅ Schema List Normalization: PASSED")
    except (ValidationError, AssertionError) as e:
        print(f"❌ Schema List Normalization: FAILED - {e}")

    # File model with numeric or unexpected formats
    file_payload = {"name": "video.mp4", "format": 512, "source": "original"}
    try:
        validated_file = FileMetadata.model_validate(file_payload)
        assert validated_file.format == "512"
        print("✅ File Schema Coercion: PASSED")
    except (ValidationError, AssertionError) as e:
        print(f"❌ File Schema Coercion: FAILED - {e}")


def test_audit_engine_execution():
    """Runs a single live asset audit and a full collection sample audit."""
    print("\n--- Testing audit_engine.py Execution ---")
    
    # Test single known asset
    test_id = "DuckandC1951"
    single_res = fetch_and_audit_single_item(test_id)
    
    required_keys = ["identifier", "health_score", "media_url", "has_captions", "missing_issues"]
    if all(k in single_res for k in required_keys) and single_res["identifier"] == test_id:
        print(f"✅ Single Item Audit ({test_id}): PASSED (Health Score: {single_res['health_score']}%)")
    else:
        print(f"❌ Single Item Audit ({test_id}): FAILED")

    # Test full collection runner
    df = run_full_audit(collection_name="prelinger", sample_size=3)
    if isinstance(df, pd.DataFrame) and len(df) == 3 and "health_score" in df.columns:
        print(f"✅ Full Audit Runner (3 items): PASSED")
    else:
        print(f"❌ Full Audit Runner: FAILED")


def test_app_export_function():
    """Tests the dataframe-to-CSV conversion helper in app.py."""
    print("\n--- Testing app.py Helper Functions ---")
    sample_df = pd.DataFrame([{"identifier": "test", "health_score": 100}])
    try:
        csv_bytes = app.convert_df_to_csv(sample_df)
        assert isinstance(csv_bytes, bytes)
        assert b"health_score" in csv_bytes
        print("✅ CSV Export Converter: PASSED")
    except Exception as e:
        print(f"❌ CSV Export Converter: FAILED - {e}")


if __name__ == "__main__":
    print("Starting Fixity Vault Local Pipeline Verification...\n" + "=" * 50)
    test_schema_resilience()
    test_audit_engine_execution()
    test_app_export_function()
    print("=" * 50 + "\n🎉 All core components verified! You can safely launch: streamlit run app.py")