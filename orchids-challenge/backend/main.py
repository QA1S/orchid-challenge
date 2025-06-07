from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from scraping import scrape_website
from llm import generate_clone_html
from models import WebsiteCloneRequest
from typing import Dict, List
import uvicorn
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Orchids Challenge API",
    description="A starter FastAPI template for the Orchids Challenge backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/clone")
async def clone_website(payload: WebsiteCloneRequest):
    try:
        logger.info(f"Starting clone process for URL: {payload.url}")
        
        # first we get the website content
        logger.info("Starting website scraping...")
        context = await scrape_website(payload.url)
        logger.info(f"Scraping completed. Context length: {len(context)} characters")
        
        # then generate HTML with some LLM
        logger.info("Starting HTML generation...")
        cloned_html = generate_clone_html(context["context"], context["screenshot"])
        logger.info(f"HTML generation completed. Output length: {len(cloned_html)} characters")

        return {"html": cloned_html}

    except Exception as e:
        # Log the full traceback for debugging
        logger.error(f"Error in clone_website: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return a more detailed error response
        raise HTTPException(
            status_code=500, 
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "An error occurred while cloning the website. Please check the logs for more details."
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Orchids API is running"}


def main():
    """Run the application"""
    uvicorn.run(
        "main:app",  # Fixed the reference here
        host="127.0.0.1",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()