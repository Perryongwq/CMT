import os
import json
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "CMT (CMT)"
    PROJECT_VERSION: str = "1.0.0"

    DBTYPE: str = os.getenv("DBTYPE")
    USER: str = os.getenv("USER")
    PASSWORD = os.getenv("PASSWORD")
    SERVER: str = os.getenv("SERVER", "localhost")
    PORT: str = os.getenv("PORT", 5432)  # default postgres port is 5432
    DB: str = os.getenv("DB", "tdd")
    DATABASE_URL = f"{DBTYPE}://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB}"

    ORIGIN: list = json.loads(os.getenv("ORIGIN"))
    PRASS_URL: str = os.getenv("PRASS_URL")
    LOT_NO_COL: str = os.getenv("LOT_NO_COL")
    CHIP_TYPE_COL: str = os.getenv("CHIP_TYPE_COL")
    CHIPTYPE: str = os.getenv("CHIPTYPE")

    REALTIMEDB: str = os.getenv("REALTIMEDB")
    TABLEID: str = os.getenv("TABLEID")

    BATCHSIZE: int = 64
    IMGSIZE: tuple = (54, 54)
    INPUTSHAPE: tuple = (54, 54, 3)
    SEED: int = 12345
    KER: tuple = (3, 3)
    SKER: tuple = (1, 1)


settings = Settings()