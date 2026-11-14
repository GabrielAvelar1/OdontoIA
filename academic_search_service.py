import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Garante uso do armazenamento de certificados do sistema Windows
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

# Dicionário de tradução/mapeamento para termos frequentes em odontologia PT -> EN
TERMOS_ODONTO_PT_EN = {
    "clareamento dental": "tooth bleaching whitening",
    "clareamento": "tooth bleaching",
    "implante dentario": "dental implants",
    "implantes dentarios": "dental implants",
    "implante": "dental implants",
    "implantes": "dental implants",
    "peri-implantite": "peri-implantitis",
    "periimplantite": "peri-implantitis",
    "periodontite": "periodontitis",
    "gengivite": "gingivitis",
    "endodontia": "endodontics",
    "tratamento de canal": "root canal treatment",
    "canal": "root canal",
    "anestesia local": "local anesthesia",
    "anestesia": "anesthesia dental",
    "anestesico": "local anesthetics",
    "anestésico": "local anesthetics",
    "lidocaina": "lidocaine",
    "articaina": "articaine",
    "mepivacaina": "mepivacaine",
    "bupivacaina": "bupivacaine",
    "gestante": "pregnancy",
    "gestantes": "pregnant women",
    "endocardite infecciosa": "infective endocarditis",
    "endocardite": "infective endocarditis",
    "profilaxia antibiotica": "antibiotic prophylaxis",
    "profilaxia": "prophylaxis",
    "carie dentaria": "dental caries",
    "carie": "dental caries",
    "cárie": "dental caries",
    "resina composta": "composite resins",
    "resina": "composite resin",
    "ortodontia": "orthodontics",
    "extracao dentaria": "tooth extraction",
    "extracao": "tooth extraction",
    "extração": "tooth extraction",
    "terceiro molar": "third molar",
    "siso": "third molar",
    "bruxismo": "bruxism",
    "dtm": "temporomandibular disorders",
    "atm": "temporomandibular joint",
    "dor orofacial": "orofacial pain"
}

def translate_query(pt_query: str) -> str:
    """Substitui termos comuns em português para inglês clínico no PubMed/Europe PMC."""
    query = pt_query.lower()
    for pt, en in sorted(TERMOS_ODONTO_PT_EN.items(), key=lambda x: len(x[0]), reverse=True):
        if pt in query:
            query = query.replace(pt, en)
    return query

def reconstruct_inverted_index_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> str:
    """Reconstrói o abstract a partir do formato inverted index do OpenAlex."""
    if not inverted_index:
        return ""
    word_pos = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_pos.append((pos, word))
    word_pos.sort(key=lambda x: x[0])
    return " ".join([w for _, w in word_pos])

class AcademicSearchService:
    def __init__(self):
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.europe_pmc_base = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        self.openalex_base = "https://api.openalex.org/works"

    def extract_mesh_keywords(self, question: str, api_key: Optional[str] = None) -> str:
        """Usa IA para extrair termos de busca precisos em inglês a partir da dúvida do usuário."""
        key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        if not key:
            return translate_query(question)

        try:
            from google import genai
            client = genai.Client(api_key=key)
            prompt = f"""Extraia de 2 a 4 termos-chave em inglês médico/odontológico ideais para busca de artigos científicos para a dúvida:
"{question}"
Responda APENAS os termos em inglês separados por espaço, sem pontuação, sem aspas e sem explicações."""

            resp = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            if resp and resp.text:
                return resp.text.strip().replace('"', '').replace('.', '')
        except Exception:
            pass

        return translate_query(question)

    # -------------------------------------------------------------
    # 1. BUSCA PUBMED / PMC
    # -------------------------------------------------------------
    def search_pubmed(self, query: str, max_results: int = 3, study_type: str = "all_evidence") -> List[Dict[str, Any]]:
        en_query = query.strip()
        filters = ["free full text[sb]"]

        if study_type == "systematic_reviews":
            filters.append("(systematic review[pt] OR meta-analysis[pt])")
        elif study_type == "guidelines":
            filters.append("(practice guideline[pt] OR guideline[pt])")
        elif study_type == "rct":
            filters.append("randomized controlled trial[pt]")
        elif study_type == "all_evidence":
            filters.append("(systematic review[pt] OR meta-analysis[pt] OR practice guideline[pt] OR randomized controlled trial[pt])")

        filter_clause = " AND " + " AND ".join(filters)
        search_terms = f"({en_query}) AND (dentistry[MeSH Terms] OR dental[All Fields]){filter_clause}"

        params = {
            "db": "pubmed",
            "term": search_terms,
            "retmode": "json",
            "retmax": str(max_results),
            "sort": "pub_date"
        }
        url = f"{self.pubmed_base}/esearch.fcgi?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
        
        id_list = []
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                id_list = data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"Erro PubMed Search: {e}")

        if not id_list:
            return []

        # Puxa os sumários
        summary_params = {"db": "pubmed", "id": ",".join(id_list), "retmode": "json"}
        sum_url = f"{self.pubmed_base}/esummary.fcgi?{urllib.parse.urlencode(summary_params)}"
        articles = []
        try:
            req_sum = urllib.request.Request(sum_url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
            with urllib.request.urlopen(req_sum, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                result = data.get("result", {})
                for pmid in id_list:
                    if pmid not in result:
                        continue
                    item = result[pmid]
                    authors = [a.get("name", "") for a in item.get("authors", []) if "name" in a]
                    authors_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
                    
                    doi = ""
                    pmcid = ""
                    for aid in item.get("articleids", []):
                        if aid.get("idtype") == "doi":
                            doi = aid.get("value", "")
                        elif aid.get("idtype") == "pmc":
                            pmcid = aid.get("value", "")

                    pubdate = item.get("pubdate", "").split(" ")[0]
                    articles.append({
                        "id": f"pubmed_{pmid}",
                        "source_repo": "PubMed Central (EUA)",
                        "repo_badge": "🇺🇸 PubMed",
                        "pmid": pmid,
                        "pmcid": pmcid,
                        "title": item.get("title", ""),
                        "authors": authors_str or "Autores não listados",
                        "journal": item.get("source", "PubMed Central"),
                        "year": pubdate,
                        "doi": doi,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "has_full_text": bool(pmcid)
                    })
        except Exception as e:
            print(f"Erro PubMed Summary: {e}")

        return articles

    # -------------------------------------------------------------
    # 2. BUSCA EUROPE PMC (EMBL-EBI)
    # -------------------------------------------------------------
    def search_europe_pmc(self, query: str, max_results: int = 3, study_type: str = "all_evidence") -> List[Dict[str, Any]]:
        en_query = query.strip()
        epmc_query = f"(dentistry OR dental) AND ({en_query}) AND OPEN_ACCESS:y"
        if study_type in ["systematic_reviews", "all_evidence"]:
            epmc_query += ' AND (KW:"systematic review" OR TITLE:"systematic review" OR KW:"clinical trial")'

        params = {
            "query": epmc_query,
            "format": "json",
            "pageSize": str(max_results),
            "resultType": "core",
            "sort": "P_PDATE_D desc"
        }
        url = f"{self.europe_pmc_base}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "OdontoIA-TCC/1.0"})

        articles = []
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                results = data.get("resultList", {}).get("result", [])
                for item in results:
                    art_id = item.get("id", "")
                    doi = item.get("doi", "")
                    title = item.get("title", "").rstrip(".")
                    authors = item.get("authorString", "Autores não informados")
                    journal = item.get("journalTitle") or item.get("journalInfo", {}).get("journal", {}).get("title", "Europe PMC")
                    year = str(item.get("pubYear", ""))
                    abstract = item.get("abstractText", "")

                    url_art = f"https://europepmc.org/article/{item.get('source', 'MED')}/{art_id}" if art_id else f"https://doi.org/{doi}"
                    
                    articles.append({
                        "id": f"epmc_{art_id}",
                        "source_repo": "Europe PMC (Europa)",
                        "repo_badge": "🇪🇺 Europe PMC",
                        "pmid": art_id if item.get("source") == "MED" else "",
                        "pmcid": item.get("pmcid", ""),
                        "title": title,
                        "authors": authors,
                        "journal": journal,
                        "year": year,
                        "doi": doi,
                        "url": url_art,
                        "abstract": abstract,
                        "has_full_text": item.get("isOpenAccess") == "Y"
                    })
        except Exception as e:
            print(f"Erro Europe PMC: {e}")

        return articles

    # -------------------------------------------------------------
    # 3. BUSCA SCIELO / PERIÓDICOS BRASILEIROS (OPENALEX)
    # -------------------------------------------------------------
    def search_scielo_brasil(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Busca artigos brasileiros (SciELO, USP, UNESP, SBPqO) na OpenAlex."""
        search_terms = f"odontologia dental {query}"
        params = {
            "search": search_terms,
            "filter": "is_oa:true,type:article,authorships.institutions.country_code:BR",
            "per-page": str(max_results),
            "sort": "publication_year:desc"
        }
        url = f"{self.openalex_base}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "OdontoIA-TCC/1.0 (mailto:estudante@odonto.edu.br)"})

        articles = []
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                results = data.get("results", [])
                for work in results:
                    title = work.get("display_name", "")
                    year = str(work.get("publication_year", ""))
                    doi = work.get("doi", "").replace("https://doi.org/", "")
                    
                    authorships = work.get("authorships", [])
                    authors_list = [a.get("author", {}).get("display_name", "") for a in authorships if a.get("author")]
                    authors_str = ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "")

                    journal = work.get("primary_location", {}).get("source", {}).get("display_name", "Revista Brasileira de Odontologia")
                    url_art = work.get("primary_location", {}).get("landing_page_url") or (f"https://doi.org/{doi}" if doi else "https://scielo.org")

                    abstract = reconstruct_inverted_index_abstract(work.get("abstract_inverted_index"))

                    articles.append({
                        "id": f"scielo_{work.get('id', '').split('/')[-1]}",
                        "source_repo": "SciELO / Literatura Brasileira (USP, UNESP, SBPqO)",
                        "repo_badge": "🇧🇷 SciELO Brasil",
                        "pmid": "",
                        "pmcid": "",
                        "title": title,
                        "authors": authors_str or "Autores Brasileiros",
                        "journal": journal,
                        "year": year,
                        "doi": doi,
                        "url": url_art,
                        "abstract": abstract,
                        "has_full_text": True
                    })
        except Exception as e:
            print(f"Erro SciELO/OpenAlex: {e}")

        return articles

    # -------------------------------------------------------------
    # 4. BUSCA UNIFICADA MULTI-BASES (PARALELA)
    # -------------------------------------------------------------
    def search_all_sources(
        self,
        query: str,
        source_filter: str = "all",
        max_per_source: int = 2,
        study_type: str = "all_evidence",
        api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executa busca em paralelo nas 3 bases (PubMed, Europe PMC, SciELO) e unifica resultados.
        """
        en_query = self.extract_mesh_keywords(query, api_key=api_key)
        all_articles = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {}

            if source_filter in ["all", "pubmed"]:
                future_to_source[executor.submit(self.search_pubmed, en_query, max_per_source, study_type)] = "pubmed"

            if source_filter in ["all", "europe_pmc"]:
                future_to_source[executor.submit(self.search_europe_pmc, en_query, max_per_source, study_type)] = "europe_pmc"

            if source_filter in ["all", "scielo"]:
                # SciELO pesquisa muito bem com o termo original e o traduzido
                future_to_source[executor.submit(self.search_scielo_brasil, query, max_per_source)] = "scielo"

            for future in as_completed(future_to_source):
                try:
                    arts = future.result()
                    all_articles.extend(arts)
                except Exception as err:
                    print(f"Erro na busca: {err}")

        # Remove duplicatas baseadas no DOI ou título semelhante
        seen_keys = set()
        unique_articles = []
        for art in all_articles:
            key = (art.get("doi") or art.get("title", "")[:35]).lower().strip()
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_articles.append(art)

        return unique_articles

    # -------------------------------------------------------------
    # 5. EXTRAÇÃO DE CHUNKS / CONTEÚDO
    # -------------------------------------------------------------
    def fetch_article_content(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai o texto e gera fragmentos estruturados para qualquer uma das bases."""
        chunks = []
        repo = article.get("source_repo", "")
        pmcid = article.get("pmcid")
        pmid = article.get("pmid")

        # 1. Se tem texto completo no PMC (PubMed ou Europe PMC)
        if pmcid:
            clean_pmc = pmcid.replace("PMC", "")
            pmc_url = f"{self.pubmed_base}/efetch.fcgi?db=pmc&id={clean_pmc}&retmode=xml"
            try:
                req = urllib.request.Request(pmc_url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
                with urllib.request.urlopen(req, timeout=12) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)

                    for sec in root.findall(".//body//sec"):
                        sec_title_elem = sec.find("title")
                        sec_title = sec_title_elem.text.strip() if sec_title_elem is not None and sec_title_elem.text else "Corpo do Artigo"
                        
                        paragraphs = []
                        for p in sec.findall(".//p"):
                            text = "".join(p.itertext()).strip()
                            if text:
                                paragraphs.append(text)
                        
                        if paragraphs:
                            full_sec_text = "\n\n".join(paragraphs)
                            words = full_sec_text.split()
                            i = 0
                            step = 300
                            while i < len(words):
                                chunk_text = " ".join(words[i:i+step])
                                chunks.append({
                                    "section": sec_title,
                                    "text": chunk_text
                                })
                                i += (step - 50)
            except Exception:
                pass

        # 2. Se for artigo SciELO ou Europe PMC com abstract em texto
        if not chunks and article.get("abstract"):
            raw_abstract = article["abstract"]
            words = raw_abstract.split()
            i = 0
            step = 300
            while i < len(words):
                chunk_text = " ".join(words[i:i+step])
                chunks.append({
                    "section": "Resumo Clínico / Achados",
                    "text": chunk_text
                })
                i += (step - 50)

        # 3. Fallback: PubMed Abstract XML
        if not chunks and pmid:
            pubmed_url = f"{self.pubmed_base}/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
            try:
                req = urllib.request.Request(pubmed_url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)

                    for abs_elem in root.findall(".//AbstractText"):
                        label = abs_elem.attrib.get("Label", "Resumo Clínico")
                        text = "".join(abs_elem.itertext()).strip()
                        if text:
                            chunks.append({
                                "section": label.capitalize(),
                                "text": text
                            })
            except Exception:
                pass

        return chunks

    def live_multi_search_and_prepare_context(
        self,
        question: str,
        source_filter: str = "all",
        api_key: Optional[str] = None,
        max_articles: int = 4
    ) -> Dict[str, Any]:
        """
        Executa a busca simultânea nas bases, extrai os fragmentos e prepara para a IA responder na hora.
        """
        en_keywords = self.extract_mesh_keywords(question, api_key=api_key)
        articles = self.search_all_sources(
            query=question,
            source_filter=source_filter,
            max_per_source=2,
            study_type="all_evidence",
            api_key=api_key
        )

        articles = articles[:max_articles]
        if not articles:
            return {"keywords": en_keywords, "articles": [], "chunks": []}

        all_chunks = []
        for art in articles:
            art_chunks = self.fetch_article_content(art)
            for c in art_chunks[:3]:
                all_chunks.append({
                    "text": c["text"],
                    "source": f"{art['authors']} ({art['year']}) - {art['journal']} [{art['repo_badge']}]",
                    "page": c.get("section", "Resumo"),
                    "doc_type": "article",
                    "title": art["title"],
                    "authors": art["authors"],
                    "journal": f"{art['journal']} ({art['repo_badge']})",
                    "year": art["year"],
                    "doi": art["doi"],
                    "url": art["url"],
                    "repo_badge": art["repo_badge"]
                })

        return {
            "keywords": en_keywords,
            "articles": articles,
            "chunks": all_chunks
        }
