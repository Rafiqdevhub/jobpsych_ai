import uvicorn
from dotenv import load_dotenv
import os
from app.main import app

def main():
    """Run the FastAPI application"""
    load_dotenv()
    
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main()
