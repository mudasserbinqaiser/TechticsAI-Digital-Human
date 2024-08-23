from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse, JSONResponse
import os
import openai
from tts import *
from demo_lip_pose import get_demo_object

app = FastAPI()

# Set the paths for the files
audio_file_path = "/root/Digital_Human/EDTalk_Digital_Human/speech.mp3"
video_file_path = "/root/Digital_Human/EDTalk_Digital_Human/res/demo_EDTalk_lip_pose.mp4"
image_path = "/root/Digital_Human/EDTalk_Digital_Human/fairy.png"
prompt_path = "/root/Digital_Human/EDTalk_Digital_Human/system_prompt.md"

# Load the system prompt
with open(prompt_path, 'r') as file:
    system_prompt = """You are an AI assistant designed to provide clear, unique and concise answers. Your responses will be converted into speech and used for lip-syncing with a Digital Human model. To ensure smooth and accurate lip-syncing:

                    Use vocabulary that is simple and easy to lip-sync. Avoid complex words or phrases that may be difficult to articulate.
                    Keep your responses under 200 tokens. This ensures the response is concise and manageable for the speech synthesis process.
                    Prioritize clarity and brevity. Make sure your answers are to the point and easy to understand.
                    If the question is repeated, then you give different and unique answer than before."""

# conversation_history = [{"role": "system", "content": system_prompt}]

@app.post("/process_input/")
async def process_input(input_text: str = Body(..., embed=True)):
    try:
        if not input_text:
            raise HTTPException(status_code=400, detail="Input text is required")

        # Generate the chatbot response
        # conversation_history.append({"role": "user", "content": input_text})
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Replace with the correct model name
            messages=[{"role": "user", "content": input_text}],
            max_tokens=300,
            temperature=0.3,
        )
        response_text = response.choices[0].message.content

        # Generate the TTS audio response
        tts_response = openai.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=response_text
        )
        audio_content = tts_response.content
        with open(audio_file_path, "wb") as file:
            file.write(audio_content)
        demo_obj = get_demo_object(image_path, audio_file_path)
        demo_obj.run()

        with open(video_file_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode('utf-8')

        return JSONResponse(content={"assistant_text": response_text,
                                     "video_bytes" : video_file_path})

    except Exception as e:
        # Log and return the error as a JSON response
        return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.get("/stream_video/")
# def stream_video():
#     def iterfile():
#         with open(video_file_path, mode="rb") as file_like:
#             yield from file_like

#     return StreamingResponse(iterfile(), media_type="video/mp4")