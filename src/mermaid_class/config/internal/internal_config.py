from typing import Protocol
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class InternalConfigProtocol(Protocol):
    DB_PW : str

class InternalConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="src/mermaid_class/config/internal/.env",
        case_sensitive=True,
        extra="forbid",  # prevents typos in env vars
    )
    DB_PW : str = Field(...,description="")
    
config: InternalConfigProtocol = InternalConfig(_env_file="src/mermaid_class/config/internal/.env")  # type: ignore
