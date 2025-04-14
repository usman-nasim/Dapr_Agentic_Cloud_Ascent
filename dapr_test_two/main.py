from fastapi import FastAPI
    
app = FastAPI()

@app.get("/")
def get_root():
	return {"message" : "Welcome to the DACA test app two"}
