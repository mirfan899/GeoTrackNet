from typing import Optional

from fastapi import UploadFile, File
from pydantic import BaseModel


class FullTarget(BaseModel):
    extract_id: Optional[bool] = False
    include_mreid: Optional[bool] = False
    extract_entities_title_description: Optional[bool] = False
    extract_entities_h14: Optional[bool] = False
    extract_categories_topics: Optional[bool] = False
