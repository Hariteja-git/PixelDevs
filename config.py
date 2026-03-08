
import os
import warnings
import google.generativeai as genai
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

def setup_keys():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY is missing in .env file!")
    else:
        
        genai.configure(api_key=api_key)

setup_keys()

def get_agent_model(role: str):
    """
    Returns the AI Model.
    FIX: Switched to 'Gemma 3 27B' which has 14,000 daily requests (Free Tier).
    """
    
    return genai.GenerativeModel('models/gemma-3-27b-it')