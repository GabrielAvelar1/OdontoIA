import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Garante uso do armazenamento de certificados do sistema Windows
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

# Dicionário ampliado de tradução/mapeamento para termos frequentes em odontologia PT -> EN
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
    """Substitui termos comuns em português para inglês clínico no PubMed."""
    query = pt_query.lower()
    for pt, en in sorted(TERMOS_ODONTO_PT_EN.items(), key=lambda x: len(x[0]), reverse=True):
        if pt in query:
            query = query.replace(pt, en)
    return query

class PubMedService:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def extract_mesh_keywords(self, question: str, api_key: Optional[str] = None) -> str:
        """
        Usa o modelo de IA para extrair termos de busca precisos em inglês (MeSH) a partir da pergunta do usuário.
        """
        key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        if not key:
            return translate_query(question)

        try:
            from google import genai
            client = genai.Client(api_key=key)
            prompt = f"""Extraia de 2 a 4 termos-chave em inglês médico/odontológico ideais para busca de artigos no PubMed para a seguinte dúvida:
"{question}"
Responda APENAS os termos em inglês separados por espaço, sem pontuação, sem aspas e sem explicações."""

            resp = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            if resp and resp.text:
                keywords = resp.text.strip().replace('"', '').replace('.', '')
                return keywords
        except Exception as e:
            print(f"Fallback para tradutor local de termos: {e}")

        return translate_query(question)

    def search_articles(
        self,
        query: str,
        max_results: int = 5,
        study_type: str = "all_evidence",
        free_full_text: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Pesquisa no PubMed filtrando por estudos com alto nível de evidência (OBE).
        """
        en_query = query.strip()
        
        # Constrói os filtros com sintaxe aceita pelo PubMed
        filters = []
        if free_full_text:
            filters.append("free full text[sb]")

        if study_type == "systematic_reviews":
            filters.append("(systematic review[pt] OR meta-analysis[pt])")
        elif study_type == "guidelines":
            filters.append("(practice guideline[pt] OR guideline[pt])")
        elif study_type == "rct":
            filters.append("randomized controlled trial[pt]")
        elif study_type == "all_evidence":
            filters.append("(systematic review[pt] OR meta-analysis[pt] OR practice guideline[pt] OR randomized controlled trial[pt])")

        filter_clause = (" AND " + " AND ".join(filters)) if filters else ""
        search_terms = f"({en_query}) AND (dentistry[MeSH Terms] OR dental[All Fields] OR oral[All Fields]){filter_clause}"

        params = {
            "db": "pubmed",
            "term": search_terms,
            "retmode": "json",
            "retmax": str(max_results),
            "sort": "pub_date"
        }

        url = f"{self.BASE_URL}/esearch.fcgi?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
        
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode())
                id_list = data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"Erro na busca PubMed: {e}")
            return []

        # Se a busca com filtros muito estritos retornar vazio, tenta termos mais amplos com free full text
        if not id_list and study_type != "any":
            fallback_terms = f"({en_query}) AND free full text[sb]"
            params["term"] = fallback_terms
            url = f"{self.BASE_URL}/esearch.fcgi?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    data = json.loads(response.read().decode())
                    id_list = data.get("esearchresult", {}).get("idlist", [])
            except Exception:
                pass

        if not id_list:
            return []

        # Busca os metadados dos artigos encontrados
        return self.get_articles_summary(id_list)

    def get_articles_summary(self, pmid_list: List[str]) -> List[Dict[str, Any]]:
        """Obtém resumo e metadados detalhados de cada PMID."""
        params = {
            "db": "pubmed",
            "id": ",".join(pmid_list),
            "retmode": "json"
        }
        url = f"{self.BASE_URL}/esummary.fcgi?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "OdontoIA-TCC/1.0"})

        articles = []
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode())
                result = data.get("result", {})
                for pmid in pmid_list:
                    if pmid not in result:
                        continue
                    item = result[pmid]
                    
                    authors_list = [a.get("name", "") for a in item.get("authors", []) if "name" in a]
                    authors_str = ", ".join(authors_list[:3])
                    if len(authors_list) > 3:
                        authors_str += " et al."

                    article_ids = item.get("articleids", [])
                    doi = ""
                    pmcid = ""
                    for aid in article_ids:
                        if aid.get("idtype") == "doi":
                            doi = aid.get("value", "")
                        elif aid.get("idtype") == "pmc":
                            pmcid = aid.get("value", "")

                    pubdate = item.get("pubdate", "")
                    year = pubdate.split(" ")[0] if pubdate else ""

                    articles.append({
                        "pmid": pmid,
                        "pmcid": pmcid,
                        "title": item.get("title", "Sem título"),
                        "authors": authors_str or "Autores não listados",
                        "journal": item.get("source", "Revista não informada"),
                        "year": year,
                        "doi": doi,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "has_pmc_full_text": bool(pmcid)
                    })
        except Exception as e:
            print(f"Erro ao buscar sumários: {e}")

        return articles

    def fetch_article_content(self, pmid: str, pmcid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extrai o conteúdo estruturado do artigo (Abstract + Seções completas se PMC estiver disponível).
        """
        chunks = []
        
        # 1. Tenta buscar texto completo do PMC se houver PMCID
        if pmcid:
            clean_pmc = pmcid.replace("PMC", "")
            pmc_url = f"{self.BASE_URL}/efetch.fcgi?db=pmc&id={clean_pmc}&retmode=xml"
            try:
                req = urllib.request.Request(pmc_url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
                with urllib.request.urlopen(req, timeout=15) as response:
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
            except Exception as e:
                print(f"Tentativa de PMC falhou, utilizando abstract: {e}")

        # 2. Se não conseguiu PMC ou vieram poucos chunks, busca o Abstract estruturado do PubMed
        if len(chunks) < 2:
            pubmed_url = f"{self.BASE_URL}/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
            try:
                req = urllib.request.Request(pubmed_url, headers={"User-Agent": "OdontoIA-TCC/1.0"})
                with urllib.request.urlopen(req, timeout=12) as response:
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
            except Exception as e:
                print(f"Erro ao extrair abstract XML: {e}")

        return chunks

    def live_search_and_prepare_context(
        self,
        question: str,
        api_key: Optional[str] = None,
        max_articles: int = 3
    ) -> Dict[str, Any]:
        """
        Fluxo autônomo em tempo real:
        1. Converte a dúvida do usuário em termos MeSH.
        2. Pesquisa artigos no PubMed (alto nível de evidência e Open Access).
        3. Extrai o conteúdo e monta os fragmentos (chunks) estruturados para resposta imediata.
        """
        mesh_query = self.extract_mesh_keywords(question, api_key=api_key)
        articles = self.search_articles(
            query=mesh_query,
            max_results=max_articles,
            study_type="all_evidence",
            free_full_text=True
        )

        if not articles:
            return {
                "keywords": mesh_query,
                "articles": [],
                "chunks": []
            }

        all_chunks = []
        for art in articles:
            art_chunks = self.fetch_article_content(art["pmid"], art.get("pmcid"))
            for c in art_chunks[:4]: # Pega os trechos mais relevantes de cada artigo
                all_chunks.append({
                    "text": c["text"],
                    "source": f"{art['authors']} ({art['year']}) - {art['journal']}",
                    "page": c.get("section", "Resumo"),
                    "doc_type": "article",
                    "title": art["title"],
                    "authors": art["authors"],
                    "journal": art["journal"],
                    "year": art["year"],
                    "doi": art["doi"],
                    "url": art["url"]
                })

        return {
            "keywords": mesh_query,
            "articles": articles,
            "chunks": all_chunks
        }
