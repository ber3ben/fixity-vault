import requests
import pandas as pd
from schema import ItemMetadata, FileMetadata

# Default fallback list in case network requests fail
FALLBACK_FILMS = [
    "DateWith1950", "DuckandC1951", "BoysBewa1961", 
    "AreYouPop1947", "ControlY1950", "Designfo1956"
]

def get_collection_identifiers(collection_name: str = "prelinger", limit: int = 20) -> list:
    """Dynamically pulls a list of item identifiers from a specific IA collection."""
    search_url = (
        f"https://archive.org/advancedsearch.php"
        f"?q=collection%3A{collection_name}"
        f"&fl[]=identifier"
        f"&rows={limit}"
        f"&output=json"
    )
    
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            docs = response.json().get("response", {}).get("docs", [])
            identifiers = [item["identifier"] for item in docs if "identifier" in item]
            if identifiers:
                return identifiers
    except Exception as e:
        print(f"Failed to query IA search API: {e}")
        
    return FALLBACK_FILMS[:limit]

def fetch_and_audit_single_item(item_id: str) -> dict:
    """Fetches metadata and extracts direct playback and thumbnail preview URLs."""
    url = f"https://archive.org/metadata/{item_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {
                "identifier": item_id, "title": "UNTITLED", "creator": "UNKNOWN",
                "date": "ND", "license": "MISSING", "tags_count": 0,
                "has_media": "No", "has_captions": "No", "has_thumbnail": None,
                "media_url": None, "thumbnail_url": None,
                "health_score": 0, "missing_issues": "Failed to fetch"
            }
        data = response.json()
    except Exception as e:
        return {
            "identifier": item_id, "title": "UNTITLED", "creator": "UNKNOWN",
            "date": "ND", "license": "MISSING", "tags_count": 0,
            "has_media": "No", "has_captions": "No", "has_thumbnail": None,
            "media_url": None, "thumbnail_url": None,
            "health_score": 0, "missing_issues": str(e)
        }

    raw_meta = data.get("metadata", {})
    raw_files = data.get("files", [])

    if "identifier" not in raw_meta:
        raw_meta["identifier"] = item_id

    clean_meta = ItemMetadata.model_validate(raw_meta)
    file_models = [FileMetadata.model_validate(f) for f in raw_files]
    
    missing_fields = []
    
    # 1. Core Metadata Checks
    if clean_meta.title == "Untitled Asset": missing_fields.append("Title")
    if clean_meta.creator == "Unknown Creator": missing_fields.append("Creator")
    if clean_meta.date == "Undated": missing_fields.append("Date")
    if not clean_meta.licenseurl: missing_fields.append("License URL")

    # 2. Extract Web-Playable Stream URL (Prioritizes H.264/MP4 & MP3)
    playable_video = None
    playable_audio = None
    fallback_media = None

    for f in file_models:
        if not f.name:
            continue
            
        fname_lower = f.name.lower()
        format_type = f.format.lower() if f.format else ""

        # Video priority: standard MP4 or H.264 derivatives
        if fname_lower.endswith(".mp4") or "512kb" in format_type or "h.264" in format_type:
            playable_video = f"https://archive.org/download/{item_id}/{f.name}"
            break
        
        # Audio priority: VBR MP3 or standard MP3 derivatives
        if not playable_audio and (fname_lower.endswith(".mp3") or "vbr mp3" in format_type):
            playable_audio = f"https://archive.org/download/{item_id}/{f.name}"

        # Generic web stream fallback (.webm, .ogv)
        if not fallback_media and fname_lower.endswith((".webm", ".ogv")):
            fallback_media = f"https://archive.org/download/{item_id}/{f.name}"

    media_url = playable_video or playable_audio or fallback_media
    has_media = media_url is not None
    if not has_media:
        missing_fields.append("Web Media Stream")

    # 3. Accessibility / Closed Captions Check
    has_captions = any(
        f.format and any(c in f.format.upper() for c in ["SUBRIP", "VTT", "CLOSED CAPTION", "TRANSCRIPT"])
        or (f.name and f.name.lower().endswith((".srt", ".vtt")))
        for f in file_models
    )
    if not has_captions:
        missing_fields.append("Closed Captions")

    # 4. Extract Thumbnail Image URL
    thumbnail_url = None
    for f in file_models:
        if f.name and f.name.lower().endswith((".jpg", ".png", ".jpeg")):
            thumbnail_url = f"https://archive.org/download/{item_id}/{f.name}"
            break
    
    # Fallback to standard IA item tile preview image
    if not thumbnail_url:
        thumbnail_url = f"https://archive.org/services/img/{item_id}"

    has_thumbnail = thumbnail_url if thumbnail_url else None
    if not has_thumbnail:
        missing_fields.append("Thumbnail Image")

    # 5. Health Score Calculation (7 checks total)
    total_checks = 7
    passed_checks = total_checks - len(missing_fields)
    health_score = int((passed_checks / total_checks) * 100)

    # Robust tag counting logic for string or list inputs
    subject_val = clean_meta.subject
    if isinstance(subject_val, list):
        tags_count = len(subject_val)
    elif isinstance(subject_val, str) and subject_val.strip():
        tags_count = len(subject_val.split(";"))
    else:
        tags_count = 0

    return {
        "identifier": clean_meta.identifier,
        "title": clean_meta.title,
        "creator": clean_meta.creator,
        "date": clean_meta.date,
        "license": clean_meta.licenseurl or "MISSING",
        "tags_count": tags_count,
        "has_media": "Yes" if has_media else "No",
        "has_captions": "Yes" if has_captions else "No",
        "has_thumbnail": has_thumbnail,
        "media_url": media_url,
        "thumbnail_url": thumbnail_url,
        "health_score": health_score,
        "missing_issues": ", ".join(missing_fields) if missing_fields else "Clean Asset"
    }

def run_full_audit(collection_name: str = "prelinger", sample_size: int = 20) -> pd.DataFrame:
    """Pull dynamic list of item IDs from a specific collection and audit each item."""
    item_ids = get_collection_identifiers(collection_name=collection_name, limit=sample_size)
    results = [fetch_and_audit_single_item(item_id) for item_id in item_ids]
    return pd.DataFrame(results)