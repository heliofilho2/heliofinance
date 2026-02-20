# Este arquivo ajuda o Railway a detectar Python
from setuptools import setup

setup(
    name="breno-finance",
    version="1.0.0",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "gspread>=5.12.0",
        "google-auth>=2.23.0",
        "python-telegram-bot>=20.0",
        "python-dotenv>=1.0.0",
    ],
)
