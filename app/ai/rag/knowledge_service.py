import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings

from app.infra.config.settings import settings
from app.infra.logging.logger import AppLogger


class KnowledgeService:
    """
    真实向量检索服务（FAISS + OpenAI Embedding）。

    说明：
    1) 首次查询若本地索引不存在，会自动构建种子知识索引；
    2) 查询时把问题转为向量后在 FAISS 中检索 TopK；
    3) 返回检索片段与来源，满足“可追溯引用”要求。
    """

    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)
        self._store_dir = Path(settings.rag_store_dir)
        self._store_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._store_dir / "knowledge.index"
        self._meta_path = self._store_dir / "knowledge_meta.json"
        self._embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
        )

    def _seed_documents(self) -> list[dict[str, str]]:
        # 这里先提供最小可运行知识库种子，后续可替换为企业文档解析结果。
        return [
            {"source": "hr_policy.md", "fragment": "年假按工龄分档：1-10天不等，需提前发起审批。"},
            {"source": "expense_policy.md", "fragment": "差旅餐费报销需上传票据，审批通过后进入财务打款。"},
            {"source": "attendance_policy.md", "fragment": "考勤异常可在3个工作日内提交补卡申请。"},
            {"source": "workflow_guide.md", "fragment": "采购申请超过5000元需额外加审。"},
        ]

    def _build_index(self) -> None:
        docs = self._seed_documents()
        texts = [d["fragment"] for d in docs]
        vecs = self._embeddings.embed_documents(texts)
        matrix = np.array(vecs, dtype="float32")
        dim = matrix.shape[1]

        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(matrix)
        index.add(matrix)
        faiss.write_index(index, str(self._index_path))
        self._meta_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
        self._logger.info("_build_index", "构建知识向量索引完成", vectors=len(docs), dim=dim)

    def _load_index(self) -> tuple[Any, list[dict[str, str]]]:
        if not self._index_path.exists() or not self._meta_path.exists():
            self._build_index()
        index = faiss.read_index(str(self._index_path))
        meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
        return index, meta

    def ask(self, question: str) -> dict:
        self._logger.info("ask", "执行知识问答（FAISS）", question=question)
        index, meta = self._load_index()

        q_vec = np.array([self._embeddings.embed_query(question)], dtype="float32")
        faiss.normalize_L2(q_vec)
        scores, ids = index.search(q_vec, k=min(3, index.ntotal))

        hits: list[dict[str, str]] = []
        for idx in ids[0]:
            if idx < 0:
                continue
            item = meta[idx]
            hits.append({"source": item["source"], "fragment": item["fragment"]})

        if not hits:
            return {"answer": "知识库中暂未命中相关内容。", "citations": []}

        answer = "；".join([h["fragment"] for h in hits])
        return {"answer": answer, "citations": hits, "scores": scores[0].tolist()}
