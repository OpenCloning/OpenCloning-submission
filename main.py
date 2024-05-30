from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from scrape import scrape_addgene_kit

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
