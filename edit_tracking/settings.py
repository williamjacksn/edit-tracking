import os
import secrets


def as_bool(value: str) -> bool:
    true_values = ('true', '1', 'yes', 'on')
    return value.lower() in true_values


class Settings:
    bootstrap_admin: str
    db: str
    debug_layout: bool
    log_format: str
    log_level: str
    openid_client_id: str
    openid_client_secret: str
    openid_discovery_document: str
    permanent_sessions: bool
    port: int
    secret_key: str
    support_email: str
    version: str

    def __init__(self):
        self.bootstrap_admin = os.getenv('BOOTSTRAP_ADMIN')
        self.db = os.getenv('DB')
        self.debug_layout = as_bool(os.getenv('DEBUG_LAYOUT', 'false'))
        self.log_format = os.getenv('LOG_FORMAT', '%(levelname)s [%(name)s] %(message)s')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.openid_client_id = os.getenv('OPENID_CLIENT_ID')
        self.openid_client_secret = os.getenv('OPENID_CLIENT_SECRET')
        self.openid_discovery_document = os.getenv('OPENID_DISCOVERY_DOCUMENT')
        self.permanent_sessions = as_bool(os.getenv('PERMANENT_SESSIONS', 'true'))
        self.port = int(os.getenv('PORT', 8080))
        self.secret_key = os.getenv('SECRET_KEY', secrets.token_bytes(32))
        self.support_email = os.getenv('SUPPORT_EMAIL')
        self.version = os.getenv('APP_VERSION', 'unknown')
