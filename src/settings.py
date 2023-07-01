import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

APP_ID = os.environ.get("SKYWAY_APP_ID")
SECRET_KEY = os.environ.get("SKYWAY_SECRET_KEY")
