from pydantic_settings import BaseSettings, SettingsConfigDict


class Theme(BaseSettings):
    light_primary: str = "#9A4F2E"
    light_accent: str = "#496B5A"
    light_secondary: str = "#C58B2B"
    light_success: str = "#43A047"
    light_info: str = "#1976D2"
    light_warning: str = "#FF6D00"
    light_error: str = "#EF5350"

    dark_primary: str = "#D47A50"
    dark_accent: str = "#7FA58F"
    dark_secondary: str = "#D9A441"
    dark_success: str = "#43A047"
    dark_info: str = "#1976D2"
    dark_warning: str = "#FF6D00"
    dark_error: str = "#EF5350"
    model_config = SettingsConfigDict(env_prefix="theme_", extra="allow")
