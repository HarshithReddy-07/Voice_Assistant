import google.generativeai as genai
from dotenv import load_dotenv
import os, json

load_dotenv("config.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # pyright: ignore[reportPrivateImportUsage] 

model = genai.GenerativeModel('gemini-2.5-flash')  # pyright: ignore[reportPrivateImportUsage] 

SYSTEM_PROMPT = """
You are Jarvis, a voice desktop assistant. Analyze the user's input and decide the action.
You have following list of commands
Commands list - [set reminder, introduce yourself, go to sleep, goodbye, search in browser, 
open browser, search in youtube, play in youtube, download from youtube, open vs, open whatsapp, 
play music, pause music, resume music, continue music, stop music, end music, send an email, get weather, 
increase brightness, decrease brightness, unmute volume, mute volume, shutdown pc, restart pc, 
get headlines, take screenshot, capture screen]

- map the user's intended action to one of the commands in the list: 
- example : if user input is stop listening to me 
            output in json as {"action" : "go to sleep"}
- for special commands like set reminder look for time mentioned and content
- 1)For set reminder : remind me at 5:30 pm about having water
        output in json as {"action" : "set reminder", "time" : "5:30 pm", "content": "have water"}
        if any among time, content is missing replace them with None
  2)for browser search : if user doesn't specify about what to search 
        output in json as {"action" : "search in browser", "search" : None}
        if user provides what to search replace None with specified name
  3)for search in youtube or play in youtube or download in youtube : if user doesn't specify what to do
        output in json as {"action" : <intended action from above list of commands>, "search" : None}
        if user provides what to search replace None with intended action
  4)for play music, ask user where to play music from : if user says local
        output in json as {"action" : "play music", "location" : "local"}
        else if user doesn't provide any location replace local with None
        else replace local with "youtube"            
  5)for weather report, if user doesn't provide any location
        output in json as {"action":"get weather", "location" : "nuzvid"}
        else if user provided city replace nuzvid with user specified city
  6)for news headlines,if user specifies like get 10 headlines or 20 headlines
        output in json as {"action" : "get headlines", "number" : <user_specified_number>}
- If unclear, that is if users input doesn't match with commands present in list and you still know answer
    output {"action": "other", "answer": your_answer}
    if you don't know answer output {"action":"other", "answer":"Task not found"}
- Output ONLY valid JSON, nothing else.
"""

def process_with_llm(user_input: str) -> dict:
    try:
        response = model.generate_content(SYSTEM_PROMPT + "\nUser: " + user_input)
        json_response = json.loads(response.text.replace("```json","").replace("```","").strip())  # Assume it outputs clean JSON
        return json_response
    except Exception as e:
        print(f"LLM error: {e}")
        return {"action": "error", "message": "Sorry, I couldn't process that."}
    
l = []    
for i in range(5):
    a = input()    
    res = process_with_llm(str(l) + a)
    print(res) 
    l.append("User : " + a)
    l.append("LLM Response : " + res["action"])   