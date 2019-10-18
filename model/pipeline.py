from pydantic import BaseModel


class PipelineSchema(BaseModel):
    id: int
    name: str

