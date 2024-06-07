from typing import Optional
from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from scrape import scrape_addgene_kit
import shutil
import tempfile
import os
from submission_reader import load_submission_folder
from models import SuccessResponse
from submit_to_github import submit_to_github

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("index.html")


@app.post("/")
async def root_form(blah: str = Form(...)):
    # Get form data
    print(blah)
    return FileResponse("bye.html")


@app.post("/validate_addgene_zip")
async def validate_addgene_zip(files: list[UploadFile]):

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Store the files in a temporary directory
        for file in files:
            file_path = os.path.join(tmpdirname, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        try:
            submission = load_submission_folder(tmpdirname)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        try:
            pr_url = submit_to_github(submission, tmpdirname)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to submit to GitHub")

        return SuccessResponse(pull_request_url=pr_url)


@app.get("/get_kit_info")
async def get_kit_info():
    return FileResponse("get_kit_info.html")


# Takes a URL and returns the HTML content of the page
@app.get("/scrape_addgene/")
async def scrape_addgene(url: str):
    if not url.startswith("https://www.addgene.org/"):
        raise HTTPException(status_code=400, detail="URL must be from Addgene")
    try:
        page_content = await scrape_addgene_kit(url)
        return HTMLResponse(page_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
