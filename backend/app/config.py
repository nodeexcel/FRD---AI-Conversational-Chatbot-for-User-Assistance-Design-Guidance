"""Application settings loaded from config.yaml."""
from pydantic import BaseModel, Field
from typing import Optional, List
from functools import lru_cache
import os


class AppConfig(BaseModel):
    """Application configuration."""
    app_name: str = "Dress Design Chatbot"
    version: str = "1.0.0"
    environment: str = "development"


class OpenAIConfig(BaseModel):
    """OpenAI configuration."""
    api_key: str = ""
    model: str = "gpt-4o"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    def __init__(self, **data):
        super().__init__(**data)
        # Strip whitespace/newlines from API key
        if self.api_key:
            self.api_key = self.api_key.strip()


class PostgresConfig(BaseModel):
    """PostgreSQL configuration."""
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "chatbot_secret"
    database: str = "chatbot_db"
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def sync_url(self) -> str:
        """Get synchronous database URL."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    """Redis configuration."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class MongoDBConfig(BaseModel):
    """MongoDB configuration."""
    url: str = "mongodb://localhost:27017"
    database: str = "chatbot_db"


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""
    type: str = "chromadb"
    host: str = "localhost"
    port: int = 8000
    persist_directory: str = "./data/vector_store"
    collection_name: str = "dress_products"
    
    @property
    def url(self) -> str:
        """Get ChromaDB HTTP URL."""
        return f"http://{self.host}:{self.port}"


class SessionConfig(BaseModel):
    """Session configuration."""
    secret_key: str = "your-secret-key-change-in-production"
    expire_minutes: int = 60


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class CORSConfig(BaseModel):
    """CORS configuration."""
    origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]


class Settings(BaseModel):
    """Main settings class."""
    app: AppConfig = Field(default_factory=AppConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    mongodb: MongoDBConfig = Field(default_factory=MongoDBConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    
    # Database URL for SQLAlchemy
    @property
    def database_url(self) -> str:
        return self.postgres.url
    
    @property
    def database_url_sync(self) -> str:
        return self.postgres.sync_url
    
    # PostgreSQL connection settings
    @property
    def postgres_host(self) -> str:
        return self.postgres.host
    
    @property
    def postgres_port(self) -> int:
        return self.postgres.port
    
    @property
    def postgres_user(self) -> str:
        return self.postgres.user
    
    @property
    def postgres_password(self) -> str:
        return self.postgres.password
    
    @property
    def postgres_db(self) -> str:
        return self.postgres.database
    
    # OpenAI settings
    @property
    def openai_api_key(self) -> str:
        return self.openai.api_key
    
    @property
    def openai_model(self) -> str:
        return self.openai.model
    
    @property
    def openai_max_tokens(self) -> int:
        return self.openai.max_tokens
    
    @property
    def openai_temperature(self) -> float:
        return self.openai.temperature
    
    # ChromaDB settings
    @property
    def chromadb_host(self) -> str:
        return self.vector_store.host if hasattr(self.vector_store, 'host') else "localhost"
    
    @property
    def chromadb_port(self) -> int:
        return self.vector_store.port if hasattr(self.vector_store, 'port') else 8000
    
    @property
    def chromadb_url(self) -> str:
        return f"http://{self.chromadb_host}:{self.chromadb_port}"
    
    @property
    def chromadb_collection(self) -> str:
        return self.vector_store.collection_name if hasattr(self.vector_store, 'collection_name') else "dress_products"
    
    # Logging settings
    @property
    def log_level(self) -> str:
        return self.logging.level


def load_config_from_yaml(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    import yaml
    
    if not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
            # Handle environment variable substitution
            if config:
                config = _process_env_vars(config)
            
            return config
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return {}


def _process_env_vars(config: dict) -> dict:
    """Process environment variables in config."""
    import re
    
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, str):
                # Handle ${VAR_NAME} format
                matches = re.findall(r'\$\{([^}]+)\}', value)
                for match in matches:
                    env_value = os.environ.get(match, "")
                    config[key] = value.replace(f"${{{match}}}", env_value)
            elif isinstance(value, (dict, list)):
                config[key] = _process_env_vars(value)
    elif isinstance(config, list):
        for i, item in enumerate(config):
            if isinstance(item, (dict, list)):
                config[i] = _process_env_vars(item)
    
    return config


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Try to load from config.yaml
    config = load_config_from_yaml("config.yaml")
    
    if config:
        # Parse nested configuration - handle both formats
        app_config = config.get("app", {})
        openai_config = config.get("openai", {})
        
        # Handle key mismatch: config.yaml uses openai_api_key but OpenAIConfig expects api_key
        if "openai_api_key" in openai_config:
            openai_config["api_key"] = openai_config.pop("openai_api_key")
        
        # Fallback to environment variables for OpenAI API key if not in config
        if not openai_config.get("api_key"):
            openai_config["api_key"] = os.environ.get("OPENAI_API_KEY", "")
        
        # Handle postgres config (can be nested or flat)
        if "postgres" in config:
            postgres_config = config.get("postgres", {})
        else:
            postgres_config = {
                "host": config.get("postgres_host", "localhost"),
                "port": config.get("postgres_port", 5432),
                "user": config.get("postgres_user", "postgres"),
                "password": config.get("postgres_password", "chatbot_secret"),
                "database": config.get("postgres_db", "chatbot_db")
            }
        
        redis_config = config.get("redis", {})
        mongodb_config = config.get("mongodb", {})
        vector_config = config.get("vector_store", {})
        
        # Handle vector_store config (can be nested or flat)
        if not vector_config:
            vector_config = {
                "type": config.get("vector_store_type", "chromadb"),
                "host": config.get("chromadb_host", "localhost"),
                "port": config.get("chromadb_port", 8000),
                "persist_directory": config.get("vector_store_path", "./data/vector_store"),
                "collection_name": config.get("chroma_collection", "dress_products")
            }
        
        session_config = config.get("session", {})
        
        # Handle logging config
        if "logging" in config:
            logging_config = config.get("logging", {})
        else:
            logging_config = {
                "level": config.get("log_level", "INFO"),
                "format": config.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            }
        
        cors_config = config.get("cors", {})
        
        return Settings(
            app=AppConfig(**app_config),
            openai=OpenAIConfig(**openai_config),
            postgres=PostgresConfig(**postgres_config),
            redis=RedisConfig(**redis_config),
            mongodb=MongoDBConfig(**mongodb_config),
            vector_store=VectorStoreConfig(**vector_config),
            session=SessionConfig(**session_config),
            logging=LoggingConfig(**logging_config),
            cors=CORSConfig(**cors_config)
        )
    
    # Return default settings
    return Settings()


# Export settings instance
settings = get_settings()
