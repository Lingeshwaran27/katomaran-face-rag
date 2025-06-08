# ──────────────────────────────────────────────────────────────────────────────
#  app.py  –  Face Recognition + MongoDB (accurate matching version)
# ──────────────────────────────────────────────────────────────────────────────
import io, os, logging
from datetime import datetime

import numpy as np
import face_recognition
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient, errors

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s"
)

# ── Environment & DB ──────────────────────────────────────────────────────────
load_dotenv()
MONGO_URI  = os.getenv("MONGO_URI")
DB_NAME    = os.getenv("DB_NAME", "katomaran")
COLL_NAME  = os.getenv("COLLECTION", "faces")

if not MONGO_URI:
    raise RuntimeError("❌  MONGO_URI missing in .env")

client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLL_NAME]

# ── Face-match hyper-parameters ───────────────────────────────────────────────
# 0.4–0.5 is a practical sweet spot for dlib-HOG encodings.  Lower ⇒ stricter.
FACE_DISTANCE_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", 0.47))

# ── FastAPI setup ─────────────────────────────────────────────────────────────
app = FastAPI(title="Katomaran Face API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helper funcs ──────────────────────────────────────────────────────────────
def encode_image(file_bytes: bytes) -> list[float] | None:
    """Return the first face-encoding in the image, or None."""
    img = face_recognition.load_image_file(io.BytesIO(file_bytes))
    enc = face_recognition.face_encodings(img)
    return enc[0].tolist() if enc else None


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root() -> dict:
    return {"msg": "API OK"}

@app.get("/entries")
def list_entries():
    return list(collection.find({}, {"_id": 0}))

@app.post("/register")
async def register(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        logging.info("Registering %s", name)
        encoding = encode_image(await file.read())
        if not encoding:
            return JSONResponse({"error": "No face found"}, status_code=400)

        # if user exists, append new encoding; else create new document
        existing = collection.find_one({"name": name})
        ts = datetime.utcnow().isoformat()

        if existing:
            collection.update_one(
                {"name": name},
                {"$push": {"encodings": encoding}, "$set": {"updated": ts}}
            )
        else:
            collection.insert_one(
                {"name": name, "encodings": [encoding], "created": ts}
            )

        return {"status": "registered", "name": name, "timestamp": ts}

    except errors.PyMongoError as e:
        logging.error("Mongo error: %s", e)
        return JSONResponse({"error": "DB error"}, status_code=500)

@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    people = list(collection.find({}, {"_id": 0}))
    if not people:
        return {"error": "No faces in database"}

    img_bytes = await file.read()
    img = face_recognition.load_image_file(io.BytesIO(img_bytes))
    locations  = face_recognition.face_locations(img)
    encodings  = face_recognition.face_encodings(img, locations)

    results = []
    for loc, unknown in zip(locations, encodings):
        # Flatten all known encodings + keep owner index
        flat_encs   = []
        owner_index = []  # parallel list to know which person each enc belongs to
        for idx, p in enumerate(people):
            for e in p["encodings"]:
                flat_encs.append(np.array(e))
                owner_index.append(idx)

        # Compute distances in one vectorised call
        distances = face_recognition.face_distance(flat_encs, unknown)
        best_idx  = int(np.argmin(distances))
        best_dist = float(distances[best_idx])

        if best_dist < FACE_DISTANCE_THRESHOLD:
            match_name = people[owner_index[best_idx]]["name"]
            confidence = round(1 - best_dist, 3)
        else:
            match_name = "Unknown"
            confidence = None

        top, right, bottom, left = loc
        results.append({
            "name": match_name,
            "box": [top, right, bottom, left],
            "confidence": confidence
        })

    return {"results": results}

@app.post("/chat")
async def chat(req: Request):
    q = (await req.json()).get("message", "").lower()
    entries = list(collection.find({}, {"_id": 0}))
    if not entries:
        return {"answer": "No registrations yet."}

    if "how many" in q and "registered" in q:
        return {"answer": f"There are {len(entries)} registered people."}

    if "last" in q:
        last = max(entries, key=lambda d: d.get("updated", d.get("created")))
        return {"answer": f"Last registered: {last['name']} at {last.get('updated', last['created'])}"}

    if "when" in q:
        for e in entries:
            if e["name"].lower() in q:
                ts = e.get("updated", e.get("created"))
                return {"answer": f"{e['name']} registered at {ts}"}
        return {"answer": "Person not found."}

    if "list" in q:
        return {"answer": "Registered: " + ", ".join(e["name"] for e in entries)}

    return {"answer": "Sorry, I didn't understand that."}
