from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator


class FileMetadata(BaseModel):
    """Schema for individual file objects within an Internet Archive item payload."""
    name: Optional[str] = Field(default=None)
    format: Optional[str] = Field(default=None)
    size: Optional[Union[int, str]] = Field(default=None)
    source: Optional[str] = Field(default=None)

    @field_validator("format", "name", mode="before")
    @classmethod
    def ensure_string_or_none(cls, v: Any) -> Optional[str]:
        """Guarantees string conversion for filenames or formats if non-string values appear."""
        if v is None:
            return None
        return str(v).strip()


class ItemMetadata(BaseModel):
    """Schema for item-level metadata returned by the Internet Archive Metadata API."""
    identifier: str = Field(..., description="Unique IA slug/identifier")
    title: str = Field(default="Untitled Asset")
    creator: str = Field(default="Unknown Creator")
    date: str = Field(default="Undated")
    licenseurl: Optional[str] = Field(default=None)
    subject: Optional[Union[List[str], str]] = Field(default=None)

    @field_validator("title", "creator", "date", mode="before")
    @classmethod
    def normalize_list_or_string_fields(cls, v: Any) -> str:
        """
        Internet Archive APIs frequently return lists for fields like creator or date
        if multiple values exist. Normalizes them into clean, comma-separated strings.
        """
        if not v:
            return cls.get_default_for_field(v)
        if isinstance(v, list):
            # Strip empty strings and join with standard separator
            cleaned = [str(item).strip() for item in v if str(item).strip()]
            return ", ".join(cleaned) if cleaned else "Unknown"
        return str(v).strip()

    @field_validator("licenseurl", mode="before")
    @classmethod
    def normalize_license(cls, v: Any) -> Optional[str]:
        """Normalizes license URLs, handling cases where IA returns lists of licenses."""
        if not v:
            return None
        if isinstance(v, list):
            return str(v[0]).strip() if v else None
        return str(v).strip()

    @field_validator("subject", mode="before")
    @classmethod
    def normalize_subject(cls, v: Any) -> Union[List[str], str, None]:
        """Preserves lists or strings while filtering out null items."""
        if not v:
            return None
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return str(v).strip()

    @classmethod
    def get_default_for_field(cls, value: Any) -> str:
        return "Untitled Asset"