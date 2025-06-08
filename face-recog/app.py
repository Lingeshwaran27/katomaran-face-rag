from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import face_recognition
from fastapi import Request
from datetime import datetime
import io
import numpy as np


app = FastAPI()

# CORS for the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REG_DB = []   # in-memory store

# ---------- ROUTES ----------

@app.get("/")
def root():
    return {"msg": "API is up"}

@app.get("/entries")
def list_entries():
    return REG_DB


@app.post("/register")
async def register(
    name: str = Form(...),          # ← tell FastAPI this comes from the form
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    # face_recognition expects a file-like object
    img = face_recognition.load_image_file(io.BytesIO(image_bytes))
    encodings = face_recognition.face_encodings(img)

    if not encodings:
        return {"error": "No face found"}

    REG_DB.append(
        {
            "name": name,
            "encoding": encodings[0].tolist(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return {"status": "registered", "name": name, "timestamp": REG_DB[-1]["timestamp"]}

@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    if not REG_DB:
        return {"error": "No faces in database"}

    image_bytes = await file.read()
    img = face_recognition.load_image_file(io.BytesIO(image_bytes))

    # Get face locations + encodings from incoming frame
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    matches_result = []

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        for person in REG_DB:
            match = face_recognition.compare_faces([np.array(person['encoding'])], face_encoding)[0]
            if match:
                matches_result.append({
                    "name": person['name'],
                    "box": [top, right, bottom, left],
                })
                break
        else:
            matches_result.append({
                "name": "Unknown",
                "box": [top, right, bottom, left],
            })

    return JSONResponse(content={"results": matches_result})



@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    query = body.get("message", "").lower()

    if not REG_DB:
        return {"answer": "No registrations yet."}

    # --- Rule-based logic ---
    if "how many" in query and "registered" in query:
        return {"answer": f"There are {len(REG_DB)} registered people."}

    elif "last" in query:
        last = REG_DB[-1]
        return {"answer": f"The last person registered was {last['name']} at {last['timestamp']}"}

    elif "when" in query:
        for entry in REG_DB:
            if entry['name'].lower() in query:
                return {"answer": f"{entry['name']} was registered at {entry['timestamp']}"}
        return {"answer": "Person not found."}

    elif "list" in query or "show all" in query:
        names = ", ".join(entry["name"] for entry in REG_DB)
        return {"answer": f"Registered people: {names}"}

    else:
        return {"answer": "Sorry, I didn't understand that. Try asking 'how many registered', 'when was X registered', or 'who was last'."}
