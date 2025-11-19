from langchain_core.tools import BaseTool
from pydantic import BaseModel, EmailStr


class SchemaSearchInput(BaseModel):
    query: str
    user_email: EmailStr = ""
    user_password: str = ""

class AgenticSchemaSearchTool(BaseTool):
    args_schema = SchemaSearchInput