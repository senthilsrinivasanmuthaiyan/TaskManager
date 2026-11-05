from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_api_key: str = "ollama"
    llm_base_url: str = "http://127.0.0.1:11434/v1"
    llm_model: str = "deepseek-r1:8b"
    github_token: str = ""
    github_api_url: str = "https://api.github.com"
    github_write_enabled: bool = False
    github_allowed_repos: str = ""
    database_path: str = "./data/superagent.db"
    app_host: str = "127.0.0.1"
    app_port: int = 8787
    max_parallel_repos: int = 4

    @property
    def allowed_repositories(self) -> set[str]:
        return {item.strip().lower() for item in self.github_allowed_repos.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
