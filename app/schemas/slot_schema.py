from pydantic import BaseModel
from datetime import datetime

class SlotBlockSchema(BaseModel):
    init_block: datetime
    end_block: datetime

    class config:
        from_attibutes = True  