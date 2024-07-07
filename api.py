from fastapi import FastAPI
import json
from models import FullTarget

app = FastAPI()


@app.post("/full_target")
async def full_target(obj: FullTarget):
    item_dict = obj.model_dump()
    # do something with item_dict
    print(item_dict)
    """
    
    """

    result = full_target_runner(
                              item_dict["url"],
                              item_dict["options"]
                              )
    return json.loads(result)
