import google.generativeai as genai
from dotenv import load_dotenv
import os, json
from groq import Groq

load_dotenv("config.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # pyright: ignore[reportPrivateImportUsage] 

model = genai.GenerativeModel('gemini-2.5-flash')  # pyright: ignore[reportPrivateImportUsage] 

try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception:
    groq_client = None

MAX_HISTORY = 30
SYSTEM_PROMPT = """
You are Jarvis, a voice-powered desktop assistant with a calm, helpful, and slightly witty personality.

COMMANDS (DO NOT INVENT NEW ONES):
["get time","set reminder","introduce yourself","go to sleep","goodbye","search in browser","open browser","search in youtube","play in youtube","download from youtube","open vs","open whatsapp","play music","pause music","resume music","continue music","stop music","end music","send an email","get weather","increase brightness","decrease brightness","mute volume","unmute volume","shutdown pc","restart pc","get headlines","take screenshot","capture screen"]

OUTPUT FORMAT:
Always return a JSON ARRAY of action objects.

Example:
[{"action":"get time"}]

RULES (FOLLOW STRICTLY):

1. ALWAYS output ONLY valid JSON. No explanations, no markdown, no extra text.

2. Analyze the FULL user input for intent.

3. If user says words like:
"forget","cancel","never mind","stop","abort","scratch that","no wait"
→ this means CANCEL previous context.

4. If input has CANCEL + NEW COMMAND:
Example: "Never mind, play music"
→
[
 {"action":"cancel"},
 {"action":"play music","source":"youtube"}
]

5. If only cancel:
[
 {"action":"cancel"}
]

6. If a command requires additional information and the user did not provide it,
DO NOT return null values.
Instead ask a clarifying question using:

{"action":"respond","text":"question here"}

7. Required information for commands:

SET REMINDER
Requires:
- time
- content

Examples of missing information:
User: "remind me at 8:30"
→ [{"action":"respond","text":"What should I remind you about?"}]

User: "remind me to drink water"
→ [{"action":"respond","text":"When should I remind you?"}]

User: "remind me at 9 40 pm about pr review"
→ [{"action":"set reminder","time":"9:40 PM","content":"PR Review"}]

SEARCH / PLAY / DOWNLOAD
Requires query.

Examples:
User: "search on youtube"
→ [{"action":"respond","text":"What should I search on YouTube?"}]

User: "download from youtube"
→ [{"action":"respond","text":"Which video should I download?"}]

PLAY MUSIC
Cases:
- local → {"action":"play music","source":"local"}
- youtube song → {"action":"play music","source":"youtube","query":"..."}
- if song missing → ask question

Example:
User: "play music"
→ [{"action":"respond","text":"What would you like me to play?"}]

Play in youtube when user specifically asks for video or play in youtube else consider it as play music command and not play in youtube.
Example:
User: "play reddy ikkada chudu from AVSR"
→ [{"action":"play music","source":"youtube","query":"reddy ikkada chudu from AVSR"}]
User: "play reddy ikkada chudu from AVSR in youtube"
→ [{"action":"play in youtube","query":"reddy ikkada chudu from AVSR"}]

GET WEATHER
Default city: nuzvid

User: "weather"
→ [{"action":"get weather","city":"nuzvid"}]

GET HEADLINES
Extract count if provided.
Default: 10

Example:
"top 5 news"
→ [{"action":"get headlines","count":5}]

BRIGHTNESS / VOLUME
If step not given → default 10.

Example:
"increase brightness"
→ [{"action":"increase brightness","step":10}]

8. If the user asks something conversational or general knowledge:
→ respond naturally

Example:
User: "what is AI?"
→ [{"action":"respond","text":"AI stands for Artificial Intelligence..."}]

9. If the input is completely unclear:
→ [{"action":"unknown","response":"I didn't understand that."}]

FINAL RULE:
Treat every input independently but be conversational when clarification is needed.

Always return a JSON ARRAY of actions.
Only JSON.
"""

def get_system_prompt():
    return SYSTEM_PROMPT

chat_history = []

def process_with_llm(user_input: str, llm: str = "groq") -> list[dict[str,str]]:
    global chat_history
    
    if llm == "groq":
        try:
            if not groq_client:
                raise Exception("Groq client not initialized")
            
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(chat_history)
            messages.append({"role": "user", "content": f"User: {user_input}"})

            response = groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.1-8b-instant",
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            text = response.choices[0].message.content.strip()
            
            chat_history.append({"role": "user", "content": f"User: {user_input}"})
            chat_history.append({"role": "assistant", "content": text})

        except Exception as e:
            print(f"Error connecting to Groq Cloud: {e}")
            return [{"action": "respond", "text": "Sir, I encountered an error connecting to my Groq brain."}]

    elif llm == "gemini":
        import google.api_core.exceptions
        try:
            full_prompt = SYSTEM_PROMPT + "\n"
            for msg in chat_history:
                if msg["role"] == "user":
                    full_prompt += msg["content"] + "\n"
                else:
                    full_prompt += "Assistant: " + msg["content"] + "\n"
            full_prompt += f"User: {user_input}"

            response = model.generate_content(full_prompt)
            text = response.text.strip()
            
            chat_history.append({"role": "user", "content": f"User: {user_input}"})
            chat_history.append({"role": "assistant", "content": text})

        except google.api_core.exceptions.ResourceExhausted as e:
            print(f"API Quota Exhausted: {e}")
            return [{"action": "respond", "text": "Sir, my API quota limit has been reached. Please try again in an hour."}]
        except Exception as e:
            print(f"LLM API Error: {e}") 
            return [{"action": "respond", "text": "Sir, I encountered an error connecting to my brain."}]
    else:
        return [{"action": "respond", "text": f"Sir, I do not recognize the LLM {llm}."}]
   
    if len(chat_history) > MAX_HISTORY:
        del chat_history[:-MAX_HISTORY]

    try:
        # Clean response: remove markdown, ```json, etc.
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        result = json.loads(text)
        
        parsed_result = result
        if isinstance(result, dict):
            for key in result:
                if isinstance(result[key], list):
                    parsed_result = result[key]
                    break
            else:
                parsed_result = [result]
                
        # Check if user cancelled to clear history
        for action in parsed_result:
            if action.get("action") == "cancel":
                chat_history.clear()
                break
                
        return parsed_result
    except json.JSONDecodeError as e:
        print(f"LLM gave invalid JSON: {text}")
        return [{"action": "unknown", "response": "Sorry, I got confused."}]

if __name__ == "__main__":    
    while True:
        a = input("User : ") 
        print(process_with_llm(a))