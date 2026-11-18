import os
import re
import json
import unicodedata
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

# Stopwords conversacionais em português que atrapalham buscas acadêmicas no SciELO/OpenAlex
PT_CONVERSATIONAL_STOPWORDS = {
    "qual", "quais", "como", "fazer", "feito", "feita", "passo", "passos", "para",
    "uma", "um", "uns", "umas", "dos", "das", "nos", "nas", "pelo", "pela", "sobre",
    "entre", "deve", "ser", "sao", "foi", "esta", "este", "isso", "aquele", "com",
    "sem", "por", "que", "quando", "onde", "segundo", "literatura", "artigos",
    "existe", "existem", "diferenca", "melhor", "pior", "pode", "podem", "fale",
    "explique", "descreva", "queria", "saber", "sobre", "protocolo", "conduta"
}

# Dicionário ampliado de tradução clínica PT -> EN (MeSH e termos livres)
TERMOS_ODONTO_PT_EN = {
    "extracao de dentes posteriores": "posterior tooth extraction molar premolar surgical technique forceps",
    "extracao de dente posterior": "posterior tooth extraction molar premolar surgical technique forceps",
    "dentes posteriores": "posterior teeth molar premolar",
    "dente posterior": "posterior tooth molar premolar",
    "dentes anteriores": "anterior teeth incisor canine",
    "extracao dentaria": "tooth extraction exodontia surgical technique",
    "extracao": "tooth extraction exodontia",
    "extração": "tooth extraction exodontia",
    "exodontia": "tooth extraction exodontia oral surgery",
    "terceiro molar": "third molar extraction impacted",
    "siso": "third molar extraction",
    "sindesmotomia": "syndestomotomy mucoperiosteal flap tooth extraction",
    "forceps": "dental extraction forceps technique",
    "fórceps": "dental extraction forceps technique",
    "alavanca": "dental elevator luxation extraction",
    "odontoseccao": "tooth sectioning coronectomy osteotomy extraction",
    "odontosecção": "tooth sectioning osteotomy extraction",
    "alveolite": "alveolar osteitis dry socket management",
    "comunicacao bucossinusal": "oroantral communication fistula closure",
    "clareamento dental": "tooth bleaching whitening sensitivity",
    "clareamento": "tooth bleaching whitening",
    "implante dentario": "dental implants osseointegration",
    "implantes dentarios": "dental implants",
    "implante": "dental implants",
    "implantes": "dental implants",
    "peri-implantite": "peri-implantitis treatment",
    "periimplantite": "peri-implantitis treatment",
    "mucosite peri-implantar": "peri-implant mucositis treatment",
    "periodontite": "periodontitis periodontal therapy scaling",
    "gengivite": "gingivitis biofilm control",
    "curetas gracey": "Gracey curettes scaling root planing periodontal",
    "raspagem": "scaling and root planing subgingival periodontal",
    "endodontia": "endodontics root canal treatment",
    "tratamento de canal": "root canal treatment endodontic preparation irrigation",
    "abertura coronaria": "endodontic access cavity preparation",
    "hipoclorito de sodio": "sodium hypochlorite root canal irrigation",
    "canal": "root canal treatment endodontics",
    "anestesia local": "dental local anesthesia nerve block technique",
    "anestesia": "dental local anesthesia nerve block",
    "anestesico": "local anesthetics dentistry dosage",
    "anestésico": "local anesthetics dentistry dosage",
    "bloqueio alveolar inferior": "inferior alveolar nerve block technique",
    "lidocaina": "lidocaine epinephrine dental anesthesia maximum dose",
    "articaina": "articaine dental anesthesia",
    "mepivacaina": "mepivacaine dental anesthesia",
    "prilocaina": "prilocaine felypressin dental anesthesia",
    "bupivacaina": "bupivacaine dental anesthesia",
    "gestante": "pregnancy pregnant women dental management local anesthesia",
    "gestantes": "pregnant women dental care anesthesia",
    "endocardite infecciosa": "infective endocarditis antibiotic prophylaxis dental",
    "endocardite": "infective endocarditis antibiotic prophylaxis dental",
    "profilaxia antibiotica": "antibiotic prophylaxis infective endocarditis dentistry",
    "profilaxia": "antibiotic prophylaxis dentistry",
    "carie dentaria": "dental caries selective caries removal",
    "carie": "dental caries",
    "cárie": "dental caries",
    "resina composta": "composite resin restoration incremental technique adhesive",
    "sistema adesivo": "dental adhesive universal selective enamel etching",
    "protecao pulpar": "pulp capping direct indirect MTA calcium hydroxide",
    "capeamento pulpar": "direct indirect pulp capping MTA calcium hydroxide",
    "resina": "composite resin restoration",
    "ortodontia": "orthodontics tooth movement",
    "bruxismo": "bruxism occlusal splint management",
    "dtm": "temporomandibular joint disorders TMD management",
    "atm": "temporomandibular joint",
    "dor orofacial": "orofacial pain management",
    "biopsia": "oral biopsy incisional excisional technique pathology",
    "biópsia": "oral biopsy incisional excisional technique",
    "ameloblastoma": "ameloblastoma odontogenic tumor",
    "ceratocisto": "odontogenic keratocyst",
    "cisto dentigero": "dentigerous cyst",
    "cisto radicular": "radicular periapical cyst"
}

HIGH_VALUE_SECTION_KEYWORDS = [
    "method", "technique", "procedure", "protocol", "surgical", "treatment",
    "result", "conclusion", "discussion", "clinical", "management", "guideline",
    "recommendation", "step", "finding", "resumo", "metodo", "resultado",
    "conclusao", "discussao", "tecnica", "conduta"
]

def normalize_str(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def clean_portuguese_keywords(pt_query: str) -> str:
    """Remove palavras conversacionais ('Qual o passo a passo de uma...') mantendo apenas substantivos e termos clínicos."""
    norm = normalize_str(pt_query)
    words = re.findall(r"[a-z0-9\-]+", norm)
    clinical_words = [w for w in words if len(w) > 2 and w not in PT_CONVERSATIONAL_STOPWORDS]
    if not clinical_words:
        return pt_query.strip()
    return " ".join(clinical_words[:6])

def translate_query_rule_based(pt_query: str) -> str:
    """Converte uma pergunta em português em termos clínicos limpos em inglês sem stopwords em português."""
    norm_q = normalize_str(pt_query)
    matched_en = []

    for pt_phrase, en_phrase in sorted(TERMOS_ODONTO_PT_EN.items(), key=lambda x: len(x[0]), reverse=True):
        norm_pt = normalize_str(pt_phrase)
        if norm_pt in norm_q:
            matched_en.append(en_phrase)
            norm_q = norm_q.replace(norm_pt, " ")

    # Se for pergunta procedimental ("passo a passo", "como fazer", "técnica"), adiciona descritores de técnica
    is_procedural = any(w in normalize_str(pt_query) for w in ["passo", "como fazer", "tecnica", "protocolo", "tempo operatorio", "instrumenta"])
    if is_procedural and "technique" not in " ".join(matched_en):
        matched_en.append("surgical technique clinical procedure")

    if matched_en:
        # Remove palavras duplicadas mantendo ordem
        all_en_words = " ".join(matched_en).split()
        unique_en = list(dict.fromkeys(all_en_words))
        return " ".join(unique_en[:8])

    # Fallback: limpa stopwords em português
    return clean_portuguese_keywords(pt_query)

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

    def build_search_plan(self, question: str, api_key: Optional[str] = None) -> Dict[str, str]:
        """
        Planejador de Busca Científica (Padrão ECC - scientific-db-pubmed-database):
        Decompõe a pergunta do usuário em:
        1. `en_broad`: Termos clínicos em inglês otimizados para PubMed e Europe PMC.
        2. `pt_clean`: Termos clínicos em português sem stopwords para SciELO Brasil.
        3. `intent`: 'procedural' (passo a passo, técnica, conduta, dose) ou 'evidence' (comparação, eficácia).
        """
        norm_q = normalize_str(question)
        is_procedural = any(
            kw in norm_q for kw in [
                "passo a passo", "como fazer", "tecnica", "protocolo", "conduta",
                "dose", "maxima", "forceps", "alavanca", "instrument", "sequencia",
                "tempos operatorios", "preparo", "indicacao", "contraindicacao"
            ]
        )
        intent = "procedural" if is_procedural else "evidence"
        pt_clean = clean_portuguese_keywords(question)
        rule_en = translate_query_rule_based(question)

        key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        if not key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    key = str(st.secrets["GEMINI_API_KEY"]).strip()
            except Exception:
                pass

        if key:
            try:
                from google import genai
                client = genai.Client(api_key=key)
                prompt = f"""Você é um especialista em busca bibliográfica odontológica no PubMed (MeSH) e SciELO.
Converta a dúvida clínica abaixo em um JSON estrito com 2 campos:
1. "en_keywords": 3 a 6 palavras-chave clínicas em INGLÊS para o PubMed (ex: "posterior tooth extraction surgical technique forceps" ou "chlorhexidine peri-implant mucositis"). NÃO use pontuação nem operadores booleanos complexos.
2. "pt_keywords": 3 a 5 palavras-chave clínicas em PORTUGUÊS para o SciELO, removendo palavras como "qual", "passo a passo", "como fazer" (ex: "exodontia dentes posteriores técnica cirúrgica fórceps").

Dúvida: "{question}"
Responda APENAS o JSON válido."""

                resp = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )
                if resp and resp.text:
                    raw = resp.text.strip()
                    if "{" in raw and "}" in raw:
                        json_str = raw[raw.find("{"):raw.rfind("}") + 1]
                        parsed = json.loads(json_str)
                        en_kw = parsed.get("en_keywords", "").strip()
                        pt_kw = parsed.get("pt_keywords", "").strip()
                        if en_kw:
                            return {
                                "en_broad": en_kw,
                                "pt_clean": pt_kw or pt_clean,
                                "intent": intent
                            }
            except Exception:
                pass

        return {
            "en_broad": rule_en,
            "pt_clean": pt_clean,
            "intent": intent
        }

    def extract_mesh_keywords(self, question: str, api_key: Optional[str] = None) -> str:
        plan = self.build_search_plan(question, api_key=api_key)
        return plan["en_broad"]

    # -------------------------------------------------------------
    # 1. BUSCA PUBMED / PMC (MULTI-PASS COM RELEVÂNCIA E FALLBACK)
    # -------------------------------------------------------------
    def search_pubmed(self, query: str, max_results: int = 3, study_type: str = "all_evidence", intent: str = "evidence") -> List[Dict[str, Any]]:
        en_query = query.strip()

        # Constrói passes de busca em cascata (do mais específico para o mais abrangente)
        search_passes = []

        if intent == "procedural":
            # Para perguntas de técnica/passo a passo, prioriza revisões clínicas, diretrizes e artigos com texto completo ordenados por RELEVÂNCIA
            search_passes.append(
                f"({en_query}) AND (dentistry[MeSH Terms] OR dental[All Fields] OR oral surgery[All Fields]) AND free full text[sb]"
            )
            search_passes.append(
                f"({en_query}) AND free full text[sb]"
            )
            search_passes.append(
                f"({en_query}) AND hasabstract[text]"
            )
        else:
            type_filter = ""
            if study_type == "systematic_reviews":
                type_filter = " AND (systematic review[pt] OR meta-analysis[pt])"
            elif study_type == "guidelines":
                type_filter = " AND (practice guideline[pt] OR guideline[pt])"
            elif study_type == "rct":
                type_filter = " AND randomized controlled trial[pt]"
            elif study_type == "all_evidence":
                type_filter = " AND (systematic review[pt] OR meta-analysis[pt] OR practice guideline[pt] OR randomized controlled trial[pt] OR review[pt])"

            search_passes.append(
                f"({en_query}) AND (dentistry[MeSH Terms] OR dental[All Fields] OR oral[All Fields]) AND free full text[sb]{type_filter}"
            )
            search_passes.append(
                f"({en_query}) AND free full text[sb]"
            )
            search_passes.append(
                f"({en_query}) AND hasabstract[text]"
            )

        id_list = []
        for pass_term in search_passes:
            params = {
                "db": "pubmed",
                "term": pass_term,
                "retmode": "json",
                "retmax": str(max_results),
                "sort": "relevance"  # Ordenação por Melhor Correspondência Semântica (Best Match)
            }
            url = f"{self.pubmed_base}/esearch.fcgi?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "OdontoMind-TCC/2.0"})
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    found_ids = data.get("esearchresult", {}).get("idlist", [])
                    for pid in found_ids:
                        if pid not in id_list:
                            id_list.append(pid)
                    if len(id_list) >= max_results:
                        id_list = id_list[:max_results]
                        break
            except Exception as e:
                print(f"Erro PubMed Search pass: {e}")

        if not id_list:
            return []

        summary_params = {"db": "pubmed", "id": ",".join(id_list), "retmode": "json"}
        sum_url = f"{self.pubmed_base}/esummary.fcgi?{urllib.parse.urlencode(summary_params)}"
        articles = []
        try:
            req_sum = urllib.request.Request(sum_url, headers={"User-Agent": "OdontoMind-TCC/2.0"})
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
                        "journal": item.get("source", "PubMed / MEDLINE"),
                        "year": pubdate,
                        "doi": doi,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "has_full_text": bool(pmcid)
                    })
        except Exception as e:
            print(f"Erro PubMed Summary: {e}")

        return articles

    # -------------------------------------------------------------
    # 2. BUSCA EUROPE PMC (EMBL-EBI — ORDENADA POR RELEVÂNCIA)
    # -------------------------------------------------------------
    def search_europe_pmc(self, query: str, max_results: int = 3, study_type: str = "all_evidence", intent: str = "evidence") -> List[Dict[str, Any]]:
        en_query = query.strip()
        # Busca inicial com foco em artigos com resumo e acesso aberto ordenados por relevância
        epmc_passes = [
            f"(dental OR dentistry OR oral) AND ({en_query}) AND (OPEN_ACCESS:y OR HAS_ABSTRACT:y)",
            f"({en_query}) AND HAS_ABSTRACT:y"
        ]

        articles = []
        for epmc_query in epmc_passes:
            params = {
                "query": epmc_query,
                "format": "json",
                "pageSize": str(max_results),
                "resultType": "core"
                # Sem sort=P_PDATE_D para usar o algoritmo oficial de RELEVÂNCIA do Europe PMC
            }
            url = f"{self.europe_pmc_base}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "OdontoMind-TCC/2.0"})

            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    results = data.get("resultList", {}).get("result", [])
                    for item in results:
                        art_id = item.get("id", "")
                        abstract = item.get("abstractText", "")
                        if not abstract and not item.get("pmcid"):
                            continue
                        doi = item.get("doi", "")
                        title = item.get("title", "").rstrip(".")
                        authors = item.get("authorString", "Autores não informados")
                        journal = item.get("journalTitle") or item.get("journalInfo", {}).get("journal", {}).get("title", "Europe PMC")
                        year = str(item.get("pubYear", ""))

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
                    if len(articles) >= max_results:
                        articles = articles[:max_results]
                        break
            except Exception as e:
                print(f"Erro Europe PMC: {e}")

        return articles

    # -------------------------------------------------------------
    # 3. BUSCA SCIELO / PERIÓDICOS BRASILEIROS (OPENALEX COM TERMOS LIMPOS)
    # -------------------------------------------------------------
    def search_scielo_brasil(self, pt_clean_query: str, en_query: str = "", max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Busca artigos brasileiros e em língua portuguesa (SciELO, USP, UNESP, UNICAMP, SBPqO) na OpenAlex,
        usando palavras-chave limpas (sem stopwords conversacionais como 'Qual o passo a passo...').
        """
        passes = [
            {
                "search": f"odontologia {pt_clean_query}",
                "filter": "is_oa:true,type:article,authorships.institutions.country_code:BR"
            },
            {
                "search": pt_clean_query,
                "filter": "is_oa:true,type:article,language:pt"
            }
        ]
        if en_query:
            passes.append({
                "search": f"dental {en_query}",
                "filter": "is_oa:true,type:article,authorships.institutions.country_code:BR"
            })

        articles = []
        seen_ids = set()

        for p in passes:
            params = {
                "search": p["search"],
                "filter": p["filter"],
                "per-page": str(max_results + 2),
                "sort": "relevance_score:desc"
            }
            url = f"{self.openalex_base}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "OdontoMind-TCC/2.0 (mailto:estudante@odonto.edu.br)"})

            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    results = data.get("results", [])
                    for work in results:
                        work_id = work.get("id", "").split("/")[-1]
                        if not work_id or work_id in seen_ids:
                            continue
                        abstract = reconstruct_inverted_index_abstract(work.get("abstract_inverted_index"))
                        title = work.get("display_name", "")
                        if not abstract and not title:
                            continue

                        seen_ids.add(work_id)
                        year = str(work.get("publication_year", ""))
                        doi = (work.get("doi") or "").replace("https://doi.org/", "")

                        authorships = work.get("authorships", [])
                        authors_list = [a.get("author", {}).get("display_name", "") for a in authorships if a.get("author")]
                        authors_str = ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "")

                        journal = (work.get("primary_location") or {}).get("source", {})
                        journal_name = journal.get("display_name", "Periódico Nacional / SciELO") if journal else "Periódico Nacional / SciELO"
                        url_art = (work.get("primary_location") or {}).get("landing_page_url") or (f"https://doi.org/{doi}" if doi else "https://scielo.br")

                        articles.append({
                            "id": f"scielo_{work_id}",
                            "source_repo": "SciELO / Literatura Brasileira (USP, UNESP, SBPqO)",
                            "repo_badge": "🇧🇷 SciELO Brasil",
                            "pmid": "",
                            "pmcid": "",
                            "title": title,
                            "authors": authors_str or "Autores Brasileiros",
                            "journal": journal_name,
                            "year": year,
                            "doi": doi,
                            "url": url_art,
                            "abstract": abstract or f"Artigo científico brasileiro intitulado: {title}, publicado em {journal_name} ({year}).",
                            "has_full_text": True
                        })
                        if len(articles) >= max_results:
                            break
                if len(articles) >= max_results:
                    break
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
        Executa busca em paralelo nas 3 bases (PubMed, Europe PMC, SciELO) usando o Planejador de Busca ECC.
        """
        plan = self.build_search_plan(query, api_key=api_key)
        en_query = plan["en_broad"]
        pt_clean = plan["pt_clean"]
        intent = plan["intent"]

        all_articles = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {}

            if source_filter in ["all", "pubmed"]:
                future_to_source[executor.submit(self.search_pubmed, en_query, max_per_source, study_type, intent)] = "pubmed"

            if source_filter in ["all", "europe_pmc"]:
                future_to_source[executor.submit(self.search_europe_pmc, en_query, max_per_source, study_type, intent)] = "europe_pmc"

            if source_filter in ["all", "scielo"]:
                future_to_source[executor.submit(self.search_scielo_brasil, pt_clean, en_query, max_per_source)] = "scielo"

            for future in as_completed(future_to_source):
                try:
                    arts = future.result()
                    all_articles.extend(arts)
                except Exception as err:
                    print(f"Erro na busca: {err}")

        # Deduplicação por DOI ou título normalizado (Padrão ECC)
        seen_keys = set()
        unique_articles = []
        for art in all_articles:
            key = (art.get("doi") or normalize_str(art.get("title", ""))[:40]).strip()
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_articles.append(art)

        return unique_articles

    # -------------------------------------------------------------
    # 5. EXTRAÇÃO DE CHUNKS E RERANKING CLÍNICO DE ARTIGO COMPLETO
    # -------------------------------------------------------------
    def fetch_article_content(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai o texto completo (PMC XML) e o resumo estruturado de qualquer base."""
        chunks = []
        pmcid = article.get("pmcid")
        pmid = article.get("pmid")

        # 1. Inclui sempre o Abstract estruturado primeiro (pois sintetiza Objetivo, Métodos, Resultados e Conclusão)
        if article.get("abstract"):
            chunks.append({
                "section": "Resumo Clínico / Abstract",
                "text": article["abstract"]
            })
        elif pmid:
            pubmed_url = f"{self.pubmed_base}/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
            try:
                req = urllib.request.Request(pubmed_url, headers={"User-Agent": "OdontoMind-TCC/2.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    for abs_elem in root.findall(".//AbstractText"):
                        label = abs_elem.attrib.get("Label", "Resumo Clínico")
                        text = "".join(abs_elem.itertext()).strip()
                        if text:
                            chunks.append({
                                "section": f"Abstract - {label.capitalize()}",
                                "text": text
                            })
            except Exception:
                pass

        # 2. Se tem texto completo no PMC (PubMed Central), extrai as seções do corpo do artigo
        if pmcid:
            clean_pmc = pmcid.replace("PMC", "")
            pmc_url = f"{self.pubmed_base}/efetch.fcgi?db=pmc&id={clean_pmc}&retmode=xml"
            try:
                req = urllib.request.Request(pmc_url, headers={"User-Agent": "OdontoMind-TCC/2.0"})
                with urllib.request.urlopen(req, timeout=12) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)

                    # Extrai também o abstract do XML do PMC se ainda não tiver
                    if not chunks:
                        for abs_p in root.findall(".//abstract//p"):
                            t = "".join(abs_p.itertext()).strip()
                            if t:
                                chunks.append({"section": "Abstract", "text": t})

                    for sec in root.findall(".//body//sec"):
                        sec_title_elem = sec.find("title")
                        sec_title = sec_title_elem.text.strip() if sec_title_elem is not None and sec_title_elem.text else "Corpo do Artigo"

                        paragraphs = []
                        for p in sec.findall("./p"):
                            text = "".join(p.itertext()).strip()
                            if text and len(text) > 40:
                                paragraphs.append(text)

                        if paragraphs:
                            full_sec_text = "\n\n".join(paragraphs)
                            words = full_sec_text.split()
                            i = 0
                            step = 320
                            while i < len(words):
                                chunk_text = " ".join(words[i:i + step])
                                chunks.append({
                                    "section": sec_title,
                                    "text": chunk_text
                                })
                                if i + step >= len(words):
                                    break
                                i += (step - 50)
            except Exception:
                pass

        return chunks

    def rerank_article_chunks(
        self,
        chunks: List[Dict[str, Any]],
        en_keywords: str,
        pt_keywords: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Reranking Semântico e Seccional:
        Em vez de pegar apenas os 3 primeiros parágrafos da Introdução, avalia TODAS as seções
        do artigo e seleciona aquelas que contêm Métodos, Técnica Cirúrgica, Resultados, Conclusões
        e maior densidade dos termos pesquisados.
        """
        if len(chunks) <= top_k:
            return chunks

        query_terms = [
            w for w in re.findall(r"[a-z0-9\-]+", normalize_str(f"{en_keywords} {pt_keywords}"))
            if len(w) > 2
        ]

        scored = []
        for idx, c in enumerate(chunks):
            sec_norm = normalize_str(c.get("section", ""))
            text_norm = normalize_str(c.get("text", ""))

            score = 0.0
            # 1. Bônus para Abstract / Resumo (visão geral completa do estudo)
            if "abstract" in sec_norm or "resumo" in sec_norm:
                score += 2.2

            # 2. Bônus para seções clínicas de alta densidade (Métodos, Técnica, Resultados, Conclusão)
            if any(h in sec_norm for h in HIGH_VALUE_SECTION_KEYWORDS):
                score += 1.6

            # 3. Penalidade leve para introduções muito longas se houver seções de métodos/resultados
            if "introduction" in sec_norm and idx > 1:
                score -= 0.4

            # 4. Densidade de termos da pergunta
            term_hits = sum(1 for t in query_terms if t in text_norm)
            score += (term_hits / max(1, len(query_terms))) * 3.0

            scored.append((score, idx, c))

        scored.sort(key=lambda x: (-x[0], x[1]))
        return [item[2] for item in scored[:top_k]]

    def live_multi_search_and_prepare_context(
        self,
        question: str,
        source_filter: str = "all",
        api_key: Optional[str] = None,
        max_articles: int = 5,
        local_rag: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Arquitetura RAG Híbrida (Padrão ECC):
        1. Planeja a busca bilíngue (MeSH em Inglês + Termos Clínicos em Português).
        2. Consulta em paralelo PubMed Central, Europe PMC e SciELO Brasil.
        3. Executa Reranking nas seções completas dos artigos (priorizando Métodos, Técnicas, Resultados e Conclusões).
        4. Combina com os protocolos clínicos relevantes do Compêndio Padrão-Ouro local (Malamed, Hupp/Peterson, Cohen, Lindhe, Baratieri, Neville).
        """
        plan = self.build_search_plan(question, api_key=api_key)
        en_keywords = plan["en_broad"]
        pt_keywords = plan["pt_clean"]
        intent = plan["intent"]

        articles = self.search_all_sources(
            query=question,
            source_filter=source_filter,
            max_per_source=2,
            study_type="all_evidence",
            api_key=api_key
        )
        articles = articles[:max_articles]

        all_chunks = []

        # 1. Se disponível, consulta também o Compêndio Padrão-Ouro e Acervo Local (Fusão Híbrida)
        if local_rag is not None:
            try:
                local_k = 3 if intent == "procedural" else 2
                local_excerpts = local_rag.search_relevant_excerpts(question, top_k=local_k)
                for lex in local_excerpts:
                    # Inclui o protocolo do livro/compêndio se tiver boa aderência lexical/semântica
                    if lex.get("hybrid_score", 0) >= 0.75 or intent == "procedural":
                        all_chunks.append(lex)
            except Exception as e:
                print(f"Aviso ao consultar RAG local na fusão híbrida: {e}")

        # 2. Extrai e faz Reranking dos artigos científicos encontrados ao vivo
        for art in articles:
            raw_chunks = self.fetch_article_content(art)
            best_chunks = self.rerank_article_chunks(
                raw_chunks,
                en_keywords=en_keywords,
                pt_keywords=pt_keywords,
                top_k=2
            )
            for c in best_chunks:
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
            "keywords": f"EN: {en_keywords} | PT: {pt_keywords}",
            "intent": "Protocolo Clínico / Passo a Passo" if intent == "procedural" else "Síntese de Evidências Científicas",
            "articles": articles,
            "chunks": all_chunks
        }
