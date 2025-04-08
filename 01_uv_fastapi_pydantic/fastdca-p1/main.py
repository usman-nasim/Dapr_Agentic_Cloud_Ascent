from fastapi import FastAPI

app : FastAPI = FastAPI()

@app.get("/")
async def get_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def get_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q" : q}



