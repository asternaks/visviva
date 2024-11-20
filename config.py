from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_mongo_uri():
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")

    # Encode username and password
    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)

    # Construct and return the MongoDB URI
    return f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.lrpt9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
