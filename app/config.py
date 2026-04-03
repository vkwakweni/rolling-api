import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class DatabaseSettings:
    app_name: str
    app_env: str

    db_host: str
    db_name: str
    db_user: str
    db_pass: str
    db_port: int

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def get_db_settings() -> DatabaseSettings:
    return DatabaseSettings(
        app_name=os.getenv("APP_NAME", "Rolling"),
        app_env=os.getenv("APP_ENV", "development"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "rolling"),
        db_user=os.getenv("DB_USER", "appuser"),
        db_pass=os.getenv("DB_PASS", ""),
    )

    
@dataclass(frozen=True)
class OpenAIClientSettings:
    api_key: str


@dataclass(frozen=True)
class OllamaClientSettings:
    ...
    

def get_ai_api_settings(model: str):
    match model:
        case "openai":
            return OpenAIClientSettings(api_key=os.getenv("OPENAI_API_KEY", ""))
        case "ollama":
            return OllamaClientSettings()

dbSettings = get_db_settings()
OpenAISettings = get_ai_api_settings("openai")
