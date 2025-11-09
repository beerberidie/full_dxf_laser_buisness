from config import DevelopmentConfig
import os

print("Current working directory:", os.getcwd())
print("DATABASE_PATH:", DevelopmentConfig.DATABASE_PATH)
print("SQLALCHEMY_DATABASE_URI:", DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
print("Database file exists:", os.path.exists(DevelopmentConfig.DATABASE_PATH))

