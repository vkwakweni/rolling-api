import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class DatabaseSettings:
    """
    A class to store the database settings.

    Attributes:
        app_name (str): Name of the application
        app_env (str): Environment of the application (e.g. "development")
        db_host (str): Database host (e.g. "localhost")
        db_name (str): Database name (e.g. "rolling")
        db_user (str): Database user (e.g. "appuser")
        db_pass (str): Database password (e.g. "")
        db_port (int): Database port (e.g. "5432")
        database_url (str): Database url (e.g. "postgresql://postgres:postgres@localhost:5432")

    """
    app_name: str
    app_env: str

    db_host: str
    db_name: str
    db_user: str
    db_pass: str
    db_port: int

    @property
    def database_url(self) -> str:
        """A database URL composed to the other class attributes."""
        return (
            f"postgresql://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def get_db_settings() -> DatabaseSettings:
    """Returns a Pydantic model for the database settings."""
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
    """
    A class to store the OpenAI API client settings.

    Attributes:
        api_key (str): OpenAI API key
    """
    api_key: str


@dataclass(frozen=True)
class OllamaClientSettings:
    """
    A class to store the Ollama API client settings.

    Attributes:
        host (str): Ollama host (e.g. "http://localhost:11434")
        model_name (str): Ollama model_name (e.g. "codellama")
        headers (dict): Ollama headers
    """
    host: str
    model_name: str
    headers: dict
    

def get_ai_api_settings(model: str):
    """Maps model names to the appropriate AI service provider client."""
    match model:
        case "openai":
            return OpenAIClientSettings(api_key=os.getenv("OPENAI_API_KEY", ""))
        case "ollama":
            return OllamaClientSettings()
        
def get_ollama_api_settings() -> OllamaClientSettings:
    """
    Creates a Pydantic model for the Ollama API settings.

    Returns:
        OllamaClientSettings: Pydantic model for the Ollama API settings
            - host (str): Ollama host (e.g. "http://localhost:11434")
            - model_name (str): Ollama model_name (e.g. "codellama")
            - headers (dict): Ollama headers containing an authorization header (e.g. {"Authorization": "Bearer token"})
    """
    return OllamaClientSettings(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                                model_name=os.getenv("OLLAMA_MODEL_NAME", "codellama"),
                                headers={"Authorization": "Bearer " + os.getenv("OLLAMA_API_KEY")})

dbSettings = get_db_settings()
OpenAISettings = get_ai_api_settings("openai")
OllamaSettings = get_ollama_api_settings()
