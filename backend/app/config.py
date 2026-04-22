from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://retrobuild:retrobuild@localhost:3306/retrobuild"
    DDRAGON_VERSION: str = "14.22.1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://localhost:4300",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
