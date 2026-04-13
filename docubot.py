"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob
import re

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        self.docs_folder = docs_folder
        self.llm_client = llm_client
        self.documents = self.load_documents()
        self.index = self.build_index(self.documents)

    def load_documents(self):
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    def build_index(self, documents):
        index = {}
        for filename, text in documents:
            words = re.findall(r"[a-z0-9]+", text.lower())
            for word in set(words):
                if word not in index:
                    index[word] = []
                if filename not in index[word]:
                    index[word].append(filename)
        return index

    def score_document(self, query, text):
        query_words = re.findall(r"[a-z0-9]+", query.lower())
        text_lower = text.lower()
        score = 0
        for word in query_words:
            if word in text_lower:
                score += 1
        return score

    def retrieve(self, query, top_k=3):
        query_words = re.findall(r"[a-z0-9]+", query.lower())
        candidate_files = set()
        for word in query_words:
            if word in self.index:
                for filename in self.index[word]:
                    candidate_files.add(filename)

        scored = []
        for filename, text in self.documents:
            if filename in candidate_files:
                score = self.score_document(query, text)
                if score > 0:
                    scored.append((score, filename, text))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [(filename, text) for _, filename, text in scored]
        return results[:top_k]

    def answer_retrieval_only(self, query, top_k=3):
        snippets = self.retrieve(query, top_k=top_k)
        if not snippets:
            return "I do not know based on these docs."
        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")
        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        if self.llm_client is None:
            raise RuntimeError("RAG mode requires an LLM client. Provide a GeminiClient instance.")
        snippets = self.retrieve(query, top_k=top_k)
        if not snippets:
            return "I do not know based on these docs."
        return self.llm_client.answer_from_snippets(query, snippets)

    def full_corpus_text(self):
        return "\n\n".join(text for _, text in self.documents)
