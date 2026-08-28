from pydantic_settings import BaseSettings, SettingsConfigDict


class Branding(BaseSettings):
    name: str = "Hearth"
    short_name: str = "Hearth"
    description: str = "Practical, step-by-step knowledge for your home and everyday life."

    model_config = SettingsConfigDict(env_prefix="hearth_brand_", extra="allow")
