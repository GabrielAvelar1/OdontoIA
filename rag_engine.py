import os
import re
import json
import unicodedata
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions
from create_sample_library import generate_sample_pdf, PDF_FILENAME

# Configurações do Banco Vetorial Local (ChromaDB)
CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), "documents")
INDEXED_ARTICLES_FILE = os.path.join(DOCUMENTS_PATH, "indexed_articles.json")

os.makedirs(DOCUMENTS_PATH, exist_ok=True)
os.makedirs(CHROMA_DATA_PATH, exist_ok=True)

PT_STOPWORDS = {
    "qual", "quais", "como", "fazer", "para", "uma", "uns", "umas", "dos", "das",
    "nos", "nas", "pelo", "pela", "sobre", "entre", "deve", "ser", "sao", "foi",
    "esta", "este", "isso", "aquele", "com", "sem", "por", "que", "quando", "onde",
    "passo", "segundo", "literatura", "odontologia", "odontologica", "clinica"
}

SYNONYM_EXPANSIONS = {
    "extracao": ["exodontia", "forceps", "alavanca", "sindesmotomia", "luxacao", "avulsao", "alveolo"],
    "exodontia": ["extracao", "forceps", "alavanca", "sindesmotomia", "luxacao", "odontoseccao"],
    "posteriores": ["molares", "pre-molares", "18r", "18l", "17", "150", "151", "furca"],
    "posterior": ["molar", "pre-molar", "18r", "18l", "17", "150", "151"],
    "canal": ["endodontia", "endodontico", "pulpectomia", "odontometria", "hipoclorito", "obturacao", "guta-percha"],
    "anestesia": ["anestesico", "lidocaina", "articaina", "mepivacaina", "bloqueio", "tubetes", "malamed"],
    "gestante": ["gravida", "trimestre", "fda", "lidocaina", "hipotensao", "supina"],
    "endocardite": ["profilaxia", "amoxicilina", "aha", "valvar", "azitromicina"],
    "gengiva": ["periodontia", "periodontite", "raspagem", "gracey", "sondagem"],
    "resina": ["adesivo", "condicionamento", "acido", "fosforico", "esmalte", "dentina", "fator-c"],
    "biopsia": ["incisional", "excisional", "formol", "lesao", "estomatologia"]
}

def normalize_text(text: str) -> str:
    """Remove acentos e converte para minúsculas para comparação lexical híbrida."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def extract_search_tokens(query: str) -> List[str]:
    """Extrai termos clínicos relevantes em português/inglês e expande sinônimos odontológicos."""
    norm = normalize_text(query)
    words = re.findall(r"[a-z0-9\-]+", norm)
    tokens = [w for w in words if len(w) > 2 and w not in PT_STOPWORDS]
    expanded = list(tokens)
    for t in tokens:
        for key, syns in SYNONYM_EXPANSIONS.items():
            if key in t:
                expanded.extend(syns)
    return list(dict.fromkeys(expanded))


class OdontoRAG:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name="acervo_odontologia",
            embedding_function=self.embedding_fn,
            metadata={"description": "Acervo de livros, diretrizes e artigos de Odontologia"}
        )
        self.ensure_seed_library()

    def ensure_seed_library(self):
        """
        Garante que o Compêndio Clínico Padrão-Ouro (9 capítulos) esteja sempre gerado e indexado,
        inclusive em deploys na nuvem (Streamlit Cloud) onde o banco vetorial inicia vazio.
        """
        compendio_path = os.path.join(DOCUMENTS_PATH, PDF_FILENAME)
        old_sample = os.path.join(DOCUMENTS_PATH, "Manual_Diretrizes_Clinicas_Odontologia_Exemplo.pdf")

        # Remove o arquivo antigo de 3 páginas se existir
        if os.path.exists(old_sample):
            try:
                os.remove(old_sample)
            except Exception:
                pass

        # Gera o Compêndio Padrão-Ouro atualizado se ainda não existir
        if not os.path.exists(compendio_path):
            try:
                generate_sample_pdf(DOCUMENTS_PATH)
            except Exception as e:
                print(f"Aviso ao gerar compêndio padrão: {e}")

        # Verifica se o Compêndio de 10 páginas já está indexado no ChromaDB
        try:
            existing = self.collection.get(where={"source": PDF_FILENAME}, limit=1)
            has_compendio = bool(existing and existing.get("ids"))
        except Exception:
            has_compendio = False

        if not has_compendio or self.collection.count() < 10:
            for fname in os.listdir(DOCUMENTS_PATH):
                if fname.lower().endswith(".pdf"):
                    fpath = os.path.join(DOCUMENTS_PATH, fname)
                    try:
                        self.add_pdf(fpath)
                    except Exception as e:
                        print(f"Erro ao indexar PDF {fname}: {e}")

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

    def chunk_text(self, text: str, chunk_size: int = 420, overlap: int = 80) -> List[str]:
        """
        Divide o texto em blocos (chunks) mantendo sobreposição para preservar contexto clínico completo.
        """
        words = text.split()
        chunks = []
        if not words:
            return chunks

        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
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
            chunks = self.chunk_text(page_info["text"], chunk_size=420, overlap=80)
            for chunk in chunks:
                chunk_id = f"{filename}_p{page_info['page']}_c{chunk_counter}"
                documents.append(chunk)
                metadatas.append({
                    "source": filename,
                    "page": str(page_info["page"]),
                    "doc_type": "pdf",
                    "chunk_id": chunk_id,
                    "title": filename.replace("_", " ").replace(".pdf", ""),
                    "authors": "Compêndio Clínico (Malamed, Hupp/Peterson, Andrade, Cohen, Lindhe, Baratieri, Neville)" if filename == PDF_FILENAME else "Bibliografia Local",
                    "journal": "Literatura Odontológica de Referência",
                    "year": "2026",
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
        Adiciona fragmentos de um artigo científico (PubMed, SciELO, Europe PMC) com metadados completos.
        """
        if not chunks:
            return 0

        documents = []
        metadatas = []
        ids = []

        art_id = article.get("id") or article.get("pmid") or "art"
        title = article.get("title", "")
        authors = article.get("authors", "")
        journal = article.get("journal", "")
        year = str(article.get("year", ""))
        doi = article.get("doi", "")
        url = article.get("url", "")
        repo_badge = article.get("repo_badge", "📄 Artigo")

        for idx, chunk in enumerate(chunks):
            chunk_id = f"art_{art_id}_c{idx}"
            sec = chunk.get("section", "Resumo/Corpo")
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
                "url": url,
                "repo_badge": repo_badge
            })
            ids.append(chunk_id)

        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        self._record_indexed_article(article, len(documents))
        return len(documents)

    def _record_indexed_article(self, article: Dict[str, Any], chunks_count: int):
        """Armazena histórico de artigos indexados para exibir no painel."""
        articles = self.get_indexed_articles()
        art_key = article.get("id") or article.get("pmid") or article.get("title")
        articles = [a for a in articles if (a.get("id") or a.get("pmid") or a.get("title")) != art_key]
        article_record = dict(article)
        article_record["chunks_count"] = chunks_count
        articles.append(article_record)
        with open(INDEXED_ARTICLES_FILE, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

    def get_indexed_articles(self) -> List[Dict[str, Any]]:
        """Retorna a lista de artigos científicos indexados."""
        if not os.path.exists(INDEXED_ARTICLES_FILE):
            return []
        try:
            with open(INDEXED_ARTICLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def search_relevant_excerpts(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca Híbrida (Semântica Vetorial ChromaDB + Reranking Lexical e Sinônimos Clínicos).
        Garante que termos específicos em português (ex: 'passo a passo extração dentes posteriores',
        'fórceps 18R', 'sindesmotomia', 'curetas Gracey') encontrem o capítulo exato com precisão máxima.
        """
        count = self.collection.count()
        if count == 0:
            self.ensure_seed_library()
            count = self.collection.count()
            if count == 0:
                return []

        # Recupera um pool amplo de candidatos para reranking híbrido
        candidate_pool_size = min(max(top_k * 4, 20), count)
        results = self.collection.query(
            query_texts=[query],
            n_results=candidate_pool_size
        )

        search_tokens = extract_search_tokens(query)
        candidates = []

        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results.get("distances", [[1.0] * len(docs)])[0]

            for doc, meta, dist in zip(docs, metas, distances):
                norm_doc = normalize_text(doc + " " + meta.get("title", ""))
                # Pontuação vetorial (menor distância = maior similaridade)
                vector_score = 1.0 / (1.0 + max(0.0, float(dist)))

                # Pontuação lexical (presença de termos clínicos e sinônimos expandidos)
                lexical_hits = 0
                for tok in search_tokens:
                    if tok in norm_doc:
                        lexical_hits += 1
                        # Bônus se o termo aparece múltiplas vezes no trecho
                        if norm_doc.count(tok) > 1:
                            lexical_hits += 0.35

                lexical_score = (lexical_hits / max(1, len(search_tokens))) * 2.5
                hybrid_score = vector_score + lexical_score

                candidates.append({
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
                    "repo_badge": meta.get("repo_badge", "📘 Compêndio/Livro"),
                    "distance": dist,
                    "hybrid_score": hybrid_score
                })

        # Ordena pelo score híbrido decrescente
        candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return candidates[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre o acervo indexado."""
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
        """Reinicia o acervo mantendo o Compêndio Padrão-Ouro disponível."""
        self.chroma_client.delete_collection("acervo_odontologia")
        self.collection = self.chroma_client.get_or_create_collection(
            name="acervo_odontologia",
            embedding_function=self.embedding_fn,
            metadata={"description": "Acervo de livros, diretrizes e artigos de Odontologia"}
        )
        if os.path.exists(INDEXED_ARTICLES_FILE):
            os.remove(INDEXED_ARTICLES_FILE)
        self.ensure_seed_library()
