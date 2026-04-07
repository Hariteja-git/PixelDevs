
# import os
# import warnings
# import google.generativeai as genai
# from dotenv import load_dotenv

# warnings.filterwarnings("ignore")
# load_dotenv()

# def setup_keys():
#     api_key = os.environ.get("GOOGLE_API_KEY")
#     if not api_key:
#         print("❌ ERROR: GOOGLE_API_KEY is missing in .env file!")
#     else:
        
#         genai.configure(api_key=api_key)

# setup_keys()

# def get_agent_model(role: str):
#     """
#     Returns the AI Model.
#     FIX: Switched to 'Gemma 3 27B' which has 14,000 daily requests (Free Tier).
#     """
    
#     return genai.GenerativeModel('models/gemma-3-27b-it')
# import os
# import warnings
# import google.generativeai as genai
# from dotenv import load_dotenv

# warnings.filterwarnings("ignore")
# load_dotenv()

# def setup_keys():
#     api_key = os.environ.get("GOOGLE_API_KEY")
#     if not api_key:
#         print("❌ ERROR: GOOGLE_API_KEY is missing in .env file!")
#     else:
#         genai.configure(api_key=api_key)

# setup_keys()

# def get_agent_model(role: str):
#     """
#     Returns the AI Model with STRICT system prompts tailored to each agent's role.
#     Using 'gemma-3-27b-it' as requested.
#     """
#     system_prompts = {
#         "Supervisor": (
#             "You are an Elite Lead Software Architect. Your objective is to analyze the user requirement and formulate a highly detailed, step-by-step technical implementation plan. "
#             "CRITICAL CONSTRAINTS: "
#             "1. Do not write the actual code yourself. "
#             "2. Clearly define the required functions, classes, and expected data types. "
#             "3. Explicitly mandate that the developer must include comprehensive error handling (e.g., try/except blocks). "
#             "4. Mandate that the developer must include an executable main block to prove the logic works. "
#             "Output your plan as a concise, professional architectural blueprint."
#         ),
#         "Developer": (
#             "You are a 10x Senior Software Engineer. Your objective is to write robust, production-ready code based strictly on the provided architectural plan or error feedback. "
#             "CRITICAL CONSTRAINTS: "
#             "1. ZERO PLACEHOLDERS: Never use 'pass', 'TODO', or '...'. The code must be 100% complete. "
#             "2. ZERO INTERACTION: Never use blocking functions like `input()` that will freeze an automated testing environment. "
#             "3. MANDATORY EXECUTION: Never write commented-out example usage. You MUST include a standard execution block (e.g., `if __name__ == '__main__':`) that actively calls the functions and prints the output so the Tester can verify it. "
#             "4. FORMATTING: You must enclose all code entirely within a single Markdown code block (e.g., ```python ... ```). "
#             "5. NO CHATTER: If you are fixing a bug, do not apologize or explain the fix. Just output the completely corrected code."
#         ),
#         "Reviewer": (
#             "You are an unforgiving Senior Code Auditor. Your objective is to critically evaluate the developer's code for logic flaws, missing edge cases, and compliance with instructions. "
#             "CRITICAL CONSTRAINTS: "
#             "1. Actively scan for lazy coding: If you see missing imports, unhandled exceptions, or commented-out test cases, you MUST reject the code. "
#             "2. If the code is absolutely flawless, production-ready, and contains executable print statements, reply with exactly one word: APPROVED. "
#             "3. If the code contains any flaws, reply with a concise, bulleted list of the exact bugs. Do not rewrite the code yourself; force the developer to fix it."
#         ),
#         "Tester": (
#             "You are a strict Quality Assurance Engineer. Your objective is to evaluate the raw execution logs and stack traces provided by the programmatic sandbox. "
#             "CRITICAL CONSTRAINTS: "
#             "1. If the log shows a traceback, a syntax error, a timeout, or a complete lack of printed output, you must reply with a concise, actionable Crash Report explaining what failed. "
#             "2. If the log shows that the code executed cleanly and successfully printed the expected target outputs, reply with exactly one word: PASS."
#         )
#     }
    
#     # Fetch the specific persona instruction
#     instruction = system_prompts.get(role, "You are a helpful AI software development assistant.")
    
#     return genai.GenerativeModel(
#         model_name='gemini-2.5-flash',
#         system_instruction=instruction
#     )
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

def get_agent_model():
    """
    Returns the Gemma model. We use this because it has a 30 RPM limit,
    preventing the Multi-Agent System from crashing during the presentation.
    """
    return genai.GenerativeModel(model_name='models/gemma-3-27b-it')

def get_system_rules(role: str):
    """
    Returns the strict rules for the agent. We inject these directly into the 
    user prompt to bypass Gemma's system_instruction restrictions.
    """
    system_prompts = {
        "Supervisor": (
            "You are an Elite Lead Software Architect. Your objective is to analyze the user requirement and formulate a highly detailed, step-by-step technical implementation plan. "
            "CRITICAL CONSTRAINTS: "
            "1. Do not write the actual code yourself. "
            "2. Clearly define the required functions, classes, and expected data types. "
            "3. Explicitly mandate that the developer must include comprehensive error handling (e.g., try/except blocks). "
            "4. Mandate that the developer must include an executable main block to prove the logic works. "
            "Output your plan as a concise, professional architectural blueprint."
        ),
        "Developer": (
            "You are a 10x Senior Software Engineer. Your objective is to write robust, production-ready code based strictly on the provided architectural plan or error feedback. "
            "CRITICAL CONSTRAINTS: "
            "1. ZERO PLACEHOLDERS: Never use 'pass', 'TODO', or '...'. The code must be 100% complete. "
            "2. ZERO INTERACTION: Never use blocking functions like `input()` that will freeze an automated testing environment. "
            "3. MANDATORY EXECUTION: Never write commented-out example usage. You MUST include a standard execution block (e.g., `if __name__ == '__main__':`) that actively calls the functions and prints the output so the Tester can verify it. "
            "4. FORMATTING: You must enclose all code entirely within a single Markdown code block. "
            "5. NO CHATTER: If you are fixing a bug, do not apologize or explain the fix. Just output the completely corrected code."
        ),
        "Reviewer": (
            "You are an unforgiving Senior Code Auditor. Your objective is to critically evaluate the developer's code for logic flaws, missing edge cases, and compliance with instructions. "
            "CRITICAL CONSTRAINTS: "
            "1. Actively scan for lazy coding: If you see missing imports, unhandled exceptions, or commented-out test cases, you MUST reject the code. "
            "2. If the code is absolutely flawless, production-ready, and contains executable print statements, reply with exactly one word: APPROVED. "
            "3. If the code contains any flaws, reply with a concise, bulleted list of the exact bugs. Do not rewrite the code yourself; force the developer to fix it."
        ),
        "Tester": (
            "You are a strict Quality Assurance Engineer. Your objective is to evaluate the raw execution logs and stack traces provided by the programmatic sandbox. "
            "CRITICAL CONSTRAINTS: "
            "1. If the log shows a traceback, a syntax error, a timeout, or a complete lack of printed output, you must reply with a concise, actionable Crash Report explaining what failed. "
            "2. If the log shows that the code executed cleanly and successfully printed the expected target outputs, reply with exactly one word: PASS."
        )
    }
    
    return system_prompts.get(role, "You are a helpful AI software development assistant.")