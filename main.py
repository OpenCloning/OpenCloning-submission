from typing import Optional
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from scrape import scrape_addgene_kit
import zipfile
import tempfile
from io import BytesIO
import os
from submission_reader import read_submission
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
async def validate_addgene_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a zip file")

    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(BytesIO(await file.read()), "r") as zip_ref:
            zip_ref.extractall(tmpdirname)
            files_in_zip = [
                entry.name for entry in os.scandir(tmpdirname) if entry.is_file()
            ]
            # The files in the zip should be a single xlsx file and any number of images in
            # jpeg, png or svg format (or no image)
            if len(files_in_zip) == 0:
                raise HTTPException(status_code=400, detail="No files in zip")
            # Get all file extensions
            file_extensions = [os.path.splitext(file)[-1] for file in files_in_zip]
            # There should be only one xlsx
            if file_extensions.count(".xlsx") != 1:
                raise HTTPException(
                    status_code=400, detail="There should be one xlsx file"
                )
            # There rest should be images
            for ext in file_extensions:
                if ext.lower() not in [".jpeg", ".png", ".svg", ".xlsx"]:
                    raise HTTPException(
                        status_code=400,
                        detail="Only jpeg, png and svg images are allowed",
                    )
            # Get the name of the xlsx file
            xlsx_file = next(f for f in files_in_zip if f.endswith(".xlsx"))
            xlsx_file = os.path.join(tmpdirname, xlsx_file)
            try:
                submission = read_submission(xlsx_file)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

            # Create PR
            # try:
            pr_url = submit_to_github(submission, tmpdirname)
            # except Exception as e:
            #     raise HTTPException(
            #         status_code=500, detail="Failed to submit to GitHub"
            #     )
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
