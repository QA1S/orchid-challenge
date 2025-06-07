from pydantic import BaseModel

class WebsiteCloneRequest(BaseModel):
    url: str
