import os
import secrets


class Settings:
    db: str
    log_format: str
    log_level: str
    openid_client_id: str
    openid_client_secret: str
    openid_discovery_document: str
    port: int
    secret_key: str
    version: str

    def __init__(self):
        self.db = os.getenv('DB')
        self.log_format = os.getenv('LOG_FORMAT', '%(levelname)s [%(name)s] %(message)s')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.openid_client_id = os.getenv('OPENID_CLIENT_ID')
        self.openid_client_secret = os.getenv('OPENID_CLIENT_SECRET')
        self.openid_discovery_document = os.getenv('OPENID_DISCOVERY_DOCUMENT')
        self.port = int(os.getenv('PORT', 8080))
        self.secret_key = os.getenv('SECRET_KEY', secrets.token_bytes(32))
        self.version = os.getenv('APP_VERSION', 'unknown')
