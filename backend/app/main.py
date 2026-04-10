from fastapi import FastAPI

app = FastAPI(title="Artha Sutra API", description="AI-powered trading system API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Artha Sutra API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
