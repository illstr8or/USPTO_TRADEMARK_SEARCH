from dotenv import load_dotenv
import os

load_dotenv()  # This reads .env and loads vars into os.environ

api_key = os.getenv("X_RAPIDAPI_KEY")
print("API Key:", api_key)