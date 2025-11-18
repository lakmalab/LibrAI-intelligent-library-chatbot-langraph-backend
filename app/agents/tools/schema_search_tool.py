from langchain_core.tools import BaseTool
from sqlalchemy import inspect, text
from typing import Any, Dict, List, Optional
from pydantic import Field
import json

from app.agents.prompts.registry import PROMPTS
from app.db.dbconnection import get_db
from app.agents.llm_provider import get_llm
from app.enums.ai_model import AiModel
from app.core.logger import get_logger

logger = get_logger("agentic_schema_search")


class AgenticSchemaSearchTool(BaseTool):
    name: str = "agentic_schema_search"
    description: str = (
        "Intelligently searches database schema using multi-stage reasoning. "
        "Handles large databases by first identifying relevant tables semantically, "
        "then fetching only necessary schema details."
    )

    table_cache: Optional[Dict[str, Any]] = Field(default=None, exclude=True)

    def _get_table_metadata(self, inspector) -> List[Dict[str, str]]:
        if self.table_cache is not None:
            return self.table_cache

        tables = inspector.get_table_names()
        metadata = []

        for table in tables:
            try:
                comment = inspector.get_table_comment(table).get("text", "")
                metadata.append({
                    "table_name": table,
                    "comment": comment or ""
                })
            except:
                metadata.append({
                    "table_name": table,
                    "comment": ""
                })

        self.table_cache = metadata
        return metadata

    def _semantic_table_selection(self, query: str, table_metadata: List[Dict]) -> List[str]:
        tables_summary = "\n".join([
            f"- {t['table_name']}: {t['comment']}" if t['comment']
            else f"- {t['table_name']}"
            for t in table_metadata[:100]
        ])

        prompt = PROMPTS.get("schema_search").format(
            query=query,tables_summary=tables_summary
        )

        llm = get_llm(model=AiModel.GPT_5_NANO, temperature=0)
        response = llm.invoke(prompt)

        try:
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            selected_tables = json.loads(content)
            logger.info(f"LLM selected tables: {selected_tables}")
            return selected_tables
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            query_lower = query.lower()
            matches = [
                t["table_name"] for t in table_metadata
                if any(word in t["table_name"].lower() for word in query_lower.split())
            ][:5]
            return matches if matches else [table_metadata[0]["table_name"]]

    def _get_detailed_schema(self, inspector, table_names: List[str]) -> List[Dict[str, Any]]:
        detailed_schema = []

        for table in table_names:
            try:
                columns = inspector.get_columns(table)
                foreign_keys = inspector.get_foreign_keys(table)
                indexes = inspector.get_indexes(table)

                db = next(get_db())
                sample_query = text(f"SELECT * FROM {table} LIMIT 3")
                sample_data = db.execute(sample_query).fetchall()

                detailed_schema.append({
                    "table": table,
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col.get("nullable", True),
                            "default": col.get("default")
                        }
                        for col in columns
                    ],
                    "foreign_keys": foreign_keys,
                    "indexes": indexes,
                    "sample_rows": len(sample_data),
                    "sample_data": [dict(row._mapping) for row in sample_data[:2]]
                })
            except Exception as e:
                logger.error(f"Error fetching schema for {table}: {e}")
                continue

        return detailed_schema



    def _run(self, query: str, **kwargs) -> Dict[str, Any]:
        db = next(get_db())
        inspector = inspect(db.bind)

        try:
            logger.info("Stage 1: Fetching table metadata...")
            table_metadata = self._get_table_metadata(inspector)
            logger.info(f"Found {len(table_metadata)} tables in database")

            logger.info("Stage 2: Semantic table selection...")
            relevant_tables = self._semantic_table_selection(query, table_metadata)
            logger.info(f"Selected {len(relevant_tables)} relevant tables: {relevant_tables}")

            logger.info("Stage 3: Fetching detailed schema...")
            detailed_schema = self._get_detailed_schema(inspector, relevant_tables)

            need_interrupt = any(
                any(col["name"].lower() == "member_id" for col in table["columns"])
                for table in detailed_schema
            )

            logger.info(f"need_to_interrupt = {need_interrupt}")

            return {
                "success": True,
                "total_tables_in_db": len(table_metadata),
                "tables_analyzed": len(relevant_tables),
                "schema": detailed_schema,
                "can_answer_query": True,
                "need_to_interrupt":need_interrupt
            }

        except Exception as e:
            logger.error(f"Agentic schema search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "can_answer_query": False
            }