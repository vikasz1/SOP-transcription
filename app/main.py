# app/main.py
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import whisper,os
import speech_recognition as sr
from fastapi.middleware.cors import CORSMiddleware
# from moviepy.editor import VideoFileClip


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize Whisper model
model = whisper.load_model("turbo")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    cleanup_files()
    html_content = """
    <html>
        <head>
            <title>Upload Video</title>
        </head>
        <body>
            <h1>Upload Video for Transcription</h1>
            <form action="/transcribe" enctype="multipart/form-data" method="post">
                <label for="file">Choose video file:</label>
                <input type="file" id="file" name="file" >
                <br><br>
                <label for="language">Language:</label>
                <input type="text" id="language" name="language" value="en" required>
                <br><br>
                <input type="submit" value="Upload">
            </form>
            <br><br>
            <h1>Upload Video for Google Transcription</h1>
            <form action="/transcribe_google" enctype="multipart/form-data" method="post">
                <label for="file">Choose video file:</label>
                <input type="file" id="file" name="file">
                <br><br>
                <label for="language">Language:</label>
                <input type="text" id="language" name="language" value="en" required>
                <br><br>
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def cleanup_files():
    input_dir = "data/input"
    output_dir = "data/output"
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Delete all files in input directory
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    
    # Delete all files in output directory
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)  # Fixed: Now using output_dir instead of input_dir
        if os.path.isfile(file_path):
            os.unlink(file_path) 
            
@app.post("/transcribe")
async def transcribe_video(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    cleanup_files()
    # Ensure directories exist
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    # Save uploaded file
    input_path = f"data/input/{file.filename}"
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    # Convert video to audio
    audio_path = f"{input_path}.wav"
    os.system(f"ffmpeg -i {input_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {audio_path}")

    # audio_path = f"{input_path}.wav"
    # video = VideoFileClip(input_path)
    # video.audio.write_audiofile(audio_path)

    # Transcribe using Whisper
    # segments, info = model.transcribe(audio_path, language=language)
    # transcript = "\n".join([segment.text for segment in segments])
    transcript = model.transcribe(f"{audio_path}")

    # Save transcript
    output_path = f"data/output/{file.filename}.txt"
    with open(output_path, "w") as f:
        f.write(transcript['text'])
    return {"filename": file.filename, "transcript": transcript["text"]}

@app.post("/transcribe_google")
async def transcribe_video_google(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    # Ensure directories exist
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    # Save uploaded file
    input_path = f"data/input/{file.filename}"
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    # Convert video to audio
    audio_path = f"{input_path}.wav"
    os.system(f"ffmpeg -i {input_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {audio_path}")

    # Transcribe using Google Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    transcript = recognizer.recognize_google(audio, language=language)

    # Save transcript
    output_path = f"data/output/{file.filename}_google.txt"
    with open(output_path, "w") as f:
        f.write(transcript)

    return {"filename": file.filename, "transcript": transcript}