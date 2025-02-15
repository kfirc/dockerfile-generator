from pydantic import BaseModel, Field


class BuildInput(BaseModel):
    dockerfile_content: str = Field(description="The content of the Dockerfile to build")


class TestContainerInput(BaseModel):
   pass

