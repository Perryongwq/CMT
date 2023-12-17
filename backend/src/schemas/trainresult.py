
from pydantic import BaseModel

class TrainingResult(BaseModel):
    g_count: int
    ng_count: int
    slide_count: int
    val_g_count: int
    val_ng_count: int
    val_slide_count: int
    model_save: str
    model_info: dict
