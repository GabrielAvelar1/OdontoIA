import os
import json
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions

# Configurações do Banco Vetorial Local (ChromaDB)
CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), "documents")
INDEXED_ARTICLES_FILE = os.path.join(DOCUMENTS_PATH, "indexed_articles.json")

os.makedirs(DOCUMENTS_PATH, exist_ok=True)
os.makedirs(CHROMA_DATA_PATH, exist_ok=True)

class OdontoRAG:
    def __init__(self):
        # Cliente persistente no disco local
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        # Função de embedding padrão local (onnx all-MiniLM-L6-v2)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name="acervo_odontologia",
            embedding_function=self.embedding_fn,
            metadata={"description": "Acervo de livros, diretrizes e artigos de Odontologia"}
        )

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extrai o texto página por página preservando o número da página para citação acadêmica.
        """
        reader = PdfReader(pdf_path)
        pages_data = []
        filename = os.path.basename(pdf_path)
        
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages_data.append({
                    "text": text,
                    "page": idx + 1,
                    "source": filename
                })
        return pages_data

    def chunk_text(self, text: str, chunk_size: int = 700, overlap: int = 150) -> List[str]:
        """
        Divide o texto em blocos (chunks) mantendo sobreposição para preservar contexto clínico.
        """
        words = text.split()
        chunks = []
        if not words:
            return chunks

        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    def add_pdf(self, pdf_path: str) -> int:
        """
        Processa um PDF, cria os chunks com metadados de fonte e página e salva no ChromaDB.
        """
        pages = self.extract_text_from_pdf(pdf_path)
        documents = []
        metadatas = []
        ids = []

        filename = os.path.basename(pdf_path)
        chunk_counter = 0

        for page_info in pages:
            chunks = self.chunk_text(page_info["text"], chunk_size=350, overlap=60)
            for chunk in chunks:
                chunk_id = f"{filename}_p{page_info['page']}_c{chunk_counter}"
                documents.append(chunk)
                metadatas.append({
                    "source": filename,
                    "page": str(page_info["page"]),
                    "doc_type": "pdf",
                    "chunk_id": chunk_id,
                    "title": filename,
                    "authors": "",
                    "journal": "",
                    "year": "",
                    "doi": "",
                    "url": ""
                })
                ids.append(chunk_id)
                chunk_counter += 1

        if documents:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        return len(documents)

    def add_article(self, article: Dict[str, Any], chunks: List[Dict[str, Any]]) -> int:
        """
        Adiciona fragmentos de um artigo científico do PubMed com metadados completos de citação.
        """
        if not chunks:
            return 0

        documents = []
        metadatas = []
        ids = []

        pmid = article.get("pmid", "sem_pmid")
        title = article.get("title", "")
        authors = article.get("authors", "")
        journal = article.get("journal", "")
        year = str(article.get("year", ""))
        doi = article.get("doi", "")
        url = article.get("url", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")

        for idx, chunk in enumerate(chunks):
            chunk_id = f"pmid_{pmid}_c{idx}"
            sec = chunk.get("section", "Resumo/Corpo")
            # Prefixa o texto com a seção para dar mais contexto semântico à IA
            contextualized_text = f"[{sec.upper()}] {chunk['text']}"
            
            documents.append(contextualized_text)
            metadatas.append({
                "source": f"{authors} ({year}) - {journal}",
                "page": sec,
                "doc_type": "article",
                "chunk_id": chunk_id,
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "doi": doi,
                "url": url
            })
            ids.append(chunk_id)

        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        # Salva registro do artigo indexado no arquivo JSON
        self._record_indexed_article(article, len(documents))
        return len(documents)

    def _record_indexed_article(self, article: Dict[str, Any], chunks_count: int):
        """Armazena histórico de artigos indexados para exibir no painel."""
        articles = self.get_indexed_articles()
        # Evita duplicatas pelo PMID
        articles = [a for a in articles if a.get("pmid") != article.get("pmid")]
        article_record = dict(article)
        article_record["chunks_count"] = chunks_count
        articles.append(article_record)
        with open(INDEXED_ARTICLES_FILE, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

    def get_indexed_articles(self) -> List[Dict[str, Any]]:
        """Retorna a lista de artigos científicos do PubMed indexados."""
        if not os.path.exists(INDEXED_ARTICLES_FILE):
            return []
        try:
            with open(INDEXED_ARTICLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def search_relevant_excerpts(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Busca semântica no banco vetorial pelos trechos mais relevantes para a pergunta.
        """
        count = self.collection.count()
        if count == 0:
            return []

        actual_k = min(top_k, count)
        results = self.collection.query(
            query_texts=[query],
            n_results=actual_k
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results.get("distances", [[0] * len(docs)])[0]

            for doc, meta, dist in zip(docs, metas, distances):
                formatted_results.append({
                    "text": doc,
                    "source": meta.get("source", "Desconhecido"),
                    "page": meta.get("page", "?"),
                    "doc_type": meta.get("doc_type", "pdf"),
                    "title": meta.get("title", ""),
                    "authors": meta.get("authors", ""),
                    "journal": meta.get("journal", ""),
                    "year": meta.get("year", ""),
                    "doi": meta.get("doi", ""),
                    "url": meta.get("url", ""),
                    "distance": dist
                })
        return formatted_results

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre o acervo indexado.
        """
        total_chunks = self.collection.count()
        pdf_files = [f for f in os.listdir(DOCUMENTS_PATH) if f.lower().endswith(('.pdf', '.txt'))]
        articles = self.get_indexed_articles()
        return {
            "total_chunks": total_chunks,
            "total_files": len(pdf_files),
            "files": pdf_files,
            "total_articles": len(articles),
            "articles": articles
        }

    def clear_database(self):
        """Limpa o acervo para reiniciar a base."""
        self.chroma_client.delete_collection("acervo_odontologia")
        self.collection = self.chroma_client.get_or_create_collection(
            name="acervo_odontologia",
            embedding_function=self.embedding_fn,
            metadata={"description": "Acervo de livros, diretrizes e artigos de Odontologia"}
        )
        if os.path.exists(INDEXED_ARTICLES_FILE):
            os.remove(INDEXED_ARTICLES_FILE)
