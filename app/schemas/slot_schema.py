from typing import Optional

from pydantic import BaseModel
from datetime import datetime

class SlotBlockSchema(BaseModel):
    user_id:Optional[int]
    init_block: datetime
    end_block: datetime

    class config:
        from_attibutes = True  