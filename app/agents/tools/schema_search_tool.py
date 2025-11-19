from langchain_core.tools import BaseTool
from sqlalchemy import inspect, text
from typing import Any, Dict, List, Optional
from pydantic import Field
import numpy as np

from app.db.dbconnection import get_db
from app.core.logger import get_logger
from langchain_community.embeddings import OllamaEmbeddings

logger = get_logger("agentic_schema_search")


class AgenticSchemaSearchTool(BaseTool):
    name: str = "agentic_schema_search"
    description: str = (
        "Searches the database schema using fast local embeddings via Ollama. "
        "Does NOT send table names or schema to LLM — completely local, fast and scalable."
    )

    table_cache: Optional[List[Dict[str, str]]] = Field(default=None, exclude=True)
    table_embeddings: Optional[Dict[str, np.ndarray]] = Field(default=None, exclude=True)


    def _get_embedder(self):
        return OllamaEmbeddings(model="nomic-embed-text")

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
        logger.info(f"Loaded {len(metadata)} tables from DB")
        return metadata

    def _build_table_embeddings(self, table_metadata):
        if self.table_embeddings is not None:
            return self.table_embeddings

        embedder = self._get_embedder()
        self.table_embeddings = {}

        table_names = [t["table_name"] for t in table_metadata]

        logger.info("Building table embeddings using Ollama...")

        vectors = embedder.embed_documents(table_names)

        for name, vec in zip(table_names, vectors):
            self.table_embeddings[name] = np.array(vec, dtype=np.float32)

        logger.info(f"Table embeddings created: {len(self.table_embeddings)} tables embedded.")
        return self.table_embeddings

    def _semantic_table_selection(self, query: str, table_metadata) -> List[str]:
        embedder = self._get_embedder()

        query_vec = np.array(embedder.embed_query(query), dtype=np.float32)

        table_embeddings = self._build_table_embeddings(table_metadata)

        scores = []
        for table_name, vec in table_embeddings.items():
            sim = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
            scores.append((table_name, float(sim)))

        scores.sort(key=lambda x: x[1], reverse=True)

        top_tables = [name for name, score in scores[:8]]

        logger.info(f"Top embedding matches for query '{query}': {top_tables}")
        return top_tables


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

    def _run(self, query: str, user_email: str = "", user_password: str = "", **kwargs) -> Dict[str, Any]:
        db = next(get_db())
        inspector = inspect(db.bind)

        try:
            logger.info("STAGE 1 - Loading table metadata...")
            table_metadata = self._get_table_metadata(inspector)

            logger.info("STAGE 2 - Embedding semantic search (no LLM)...")
            relevant_tables = self._semantic_table_selection(query, table_metadata)

            logger.info(f"Selected {len(relevant_tables)} relevant tables: {relevant_tables}")

            logger.info("STAGE 3 - Fetching detailed schema for selected tables...")
            detailed_schema = self._get_detailed_schema(inspector, relevant_tables)

            need_interrupt = False
            if not user_email or not user_password:
                need_interrupt = any(
                    any(col["name"].lower() == "member_id" for col in table["columns"])
                    for table in detailed_schema
                )

            return {
                "success": True,
                "total_tables_in_db": len(table_metadata),
                "tables_analyzed": len(relevant_tables),
                "schema": detailed_schema,
                "can_answer_query": True,
                "need_to_interrupt": need_interrupt,
            }

        except Exception as e:
            logger.error(f"Agentic schema search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "can_answer_query": False,
            }
