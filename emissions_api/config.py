from os import environ, path
import configparser

basedir = path.abspath(path.dirname(__file__))

# Load configuration values from config.ini (treat as .env)
_config_parser = configparser.ConfigParser()
_config_file_path = path.join(basedir, 'config.ini')
_config_parser.read(_config_file_path)

def _get_ini(section: str, option: str, fallback: str = None):
    if _config_parser.has_option(section, option):
        return _config_parser.get(section, option)
    return fallback

class Config(object):
    """ base configuration """
    # Prefer environment variables; fallback to config.ini [mysql]
    RDS_MYSQL_HOST = environ.get("RDS_MYSQL_HOST") or _get_ini('mysql', 'host')
    RDS_MYSQL_PORT = environ.get("RDS_MYSQL_PORT") or _get_ini('mysql', 'port')
    RDS_MYSQL_USER = environ.get("RDS_MYSQL_USER") or _get_ini('mysql', 'user')
    RDS_MYSQL_PASS = environ.get("RDS_MYSQL_PASS") or _get_ini('mysql', 'pass')
    RDS_MYSQL_DB = environ.get("RDS_MYSQL_DB") or _get_ini('mysql', 'database')

    REDIS_HOST = environ.get("REDIS_HOST") or _get_ini('redis', 'host')
    REDIS_PORT = environ.get("REDIS_PORT") or _get_ini('redis', 'port')
    REDIS_DATABASE = environ.get("REDIS_DATABASE") or _get_ini('redis', 'database')
    REDIS_PASSWORD = environ.get("REDIS_PASSWORD") or _get_ini('redis', 'password')

class ProductionConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    ENV = "development"
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True