import asyncio
import os
import sys
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from Algorithm.audio_text_llm.service.audio_to_text import audio_to_text_model
from Algorithm.question_answering_llm.service.chat_bot import chatbot
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from Service.common.request import Request
from Service.common.response import Response
from Service.common.subject_information import SubjectInformation
from Service.database.mogodb import *
from typing import DefaultDict

app = FastAPI()

transcriptions = []
transcription_storage = {"transcription": " "}
app.mount("/static", StaticFiles(directory="static"), name="static")
audio_queue = asyncio.Queue()
student_id_info = str
active_websockets = set()  # Track active WebSocket connections
database_data_saved = DefaultDict()

@app.get("/")
async def get():
    with open("static/index.html", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content)

@app.post("/subject-information", response_model = SubjectInformation)
async def student_info(info: SubjectInformation):
    global student_id_info
    student_id_info = info.subject_id
    print(info.subject_id)
    print(student_id_info)
    database_data_saved[student_id_info] = {"Student Name": info.subject_name, "Student age": info.subject_age,"Student Gender": info.subject_gender}

    return info

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            # Put the data in the queue for processing
            await audio_queue.put(data)
    except WebSocketDisconnect:
        print("Client disconnected")
        global student_id_info
        active_websockets.remove(websocket)
        full_transcription = " ".join(transcriptions)
        transcription_storage['transcription'] = full_transcription
        database_data_saved[student_id_info]['Transcribed_Data'] = transcription_storage['transcription']
        print("Database", database_data_saved)
        print("Full transcription:", transcription_storage['transcription'])

async def process_audio_queue():
    while True:
        data = await audio_queue.get()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(data)
            temp_file_path = temp_file.name

        try:
            message = audio_to_text_model(temp_file_path)
            transcriptions.append(message)
            # Send the transcription to all connected WebSocket clients
            for websocket in active_websockets:
                await websocket.send_text(message)
        except Exception as e:
            print(f"Error processing audio: {e}")
        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except PermissionError as e:
                    print(f"PermissionError: {e}. Retrying after a small delay...")
                    await asyncio.sleep(1)  # Delay before retrying
                    try:
                        os.remove(temp_file_path)
                    except Exception as ex:
                        print(f"Failed to remove the file again: {ex}")

# Start the audio queue processing task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_audio_queue())

@app.post("/chat", response_model = Response)
async def chat_model(request: Request):
    full_transcription = transcription_storage["transcription"]
    global student_id_info
    if not full_transcription:
        return {"response": "No transcription available. Please upload an audio file first."}

    response_text = chatbot(query = request.prompt, context = full_transcription)

    if student_id_info is not None:
        database_data_saved[student_id_info]['question_answers'].append({
            "prompt": request.prompt,
            "answer": response_text.response
        })
    else:
        print("Student ID is not initialized")

    return Response(response = response_text.response)





@app.post("/end_session")
async def end_session():
    if database_data_saved:
        collection.insert_many(database_data_saved)
        
        return {"status": "Session data saved and cleared"}
    else:
        return {"status": "Session not found"}