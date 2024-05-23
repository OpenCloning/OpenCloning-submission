from typing import Optional

from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


@app.get("/")
async def root():
    return FileResponse("index.html")


@app.post("/")
async def root_form(blah: str = Form(...)):
    # Get form data
    print(blah)
    return FileResponse("bye.html")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
