from app import app
from dotenv import load_dotenv

load_dotenv('.env')

if __name__ == "__main":
    app.run()