import os


class Config:
    # Base de datos
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'sistema_dental')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

    # Aplicación
    APP_TITLE = 'Sonrisa perfecta'
    APP_VERSION = '1.1.0'
    APP_PORT = int(os.getenv('PORT', '8080'))
    STORAGE_SECRET = os.getenv('STORAGE_SECRET', 'sonrisa-perfecta-desarrollo')

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


config = Config()
