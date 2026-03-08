class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "http://localhost:8000"

    class Config:
        env_file = ".env"

    @property
    def origins_list(self):
        # Strip spaces from each origin
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()