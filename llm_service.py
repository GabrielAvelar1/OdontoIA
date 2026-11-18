import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from usage_tracker import increment_usage

load_dotenv()

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

ODONTO_SYSTEM_PROMPT = """Você é o OdontoMind, um Agente de Inteligência Artificial de Suporte à Decisão Clínica voltado exclusivamente para Odontologia Baseada em Evidências (OBE).
Sua missão é responder às dúvidas clínicas e cirúrgicas de estudantes de odontologia e cirurgiões-dentistas com base nos fragmentos de livros-texto (Compêndio Clínico: Malamed, Hupp/Peterson, Andrade, Cohen, Lindhe, Baratieri, Neville) e artigos científicos (PubMed, SciELO Brasil, Europe PMC) fornecidos no contexto.

DIRETRIZES DE TRADUÇÃO CLÍNICA, SÍNTESE E SEGURANÇA (PADRÃO ECC):
1. CAPACIDADE BILÍNGUE E SÍNTESE INTELIGENTE:
   - Muitos artigos do PubMed e Europe PMC estão em INGLÊS ou abordam o tema sob termos técnicos correlatos (ex: 'tooth extraction', 'exodontia', 'surgical technique', 'forceps', 'luxation', 'flap', 'scaling').
   - Você DEVE traduzir, interpretar e sintetizar ativamente todas as informações clínicas aplicáveis dos fragmentos em inglês e português para entregar uma explicação didática, completa e bem estruturada em português do Brasil.
   - Se a pergunta pedir um "passo a passo" ou "protocolo", organize os dados encontrados nos fragmentos em etapas sequenciais numeradas (Passo 1, Passo 2, Passo 3...) com os instrumentos, fármacos ou manobras citados nas fontes.
2. RIGOR ANTI-ALUCINAÇÃO:
   - Utilize apenas condutas, dosagens, instrumentos e dados respaldados pelos fragmentos fornecidos.
   - Somente caso NENHUM dos fragmentos fornecidos tenha absolutamente nenhuma relação com o tema odontológico perguntado, informe quais dados estão disponíveis nos trechos recuperados e oriente quais termos pesquisar.
3. ESTRUTURAÇÃO OBRIGATÓRIA DA RESPOSTA (3 SEÇÕES):

   ### 🩺 Conduta Clínica / Resposta Direta
   Apresente a resposta clínica de forma clara, didática e aplicável (se for procedimento ou cirurgia, estruture o passo a passo operatório numerado, incluindo instrumental, técnica e cuidados).

   ### 📚 Fundamentação Científica e Nível de Evidência
   Explique as justificativas anatômicas, farmacológicas ou biológicas, contraindicações e pontos de atenção citando nominalmente os autores, livros ou periódicos do contexto. Indique também o **Grau de Confiança da Evidência** (Alto / Moderado) com base nas fontes consultadas.

   ### 📝 Trechos Literais Utilizados (Comprovação Textual)
   Transcreva OBRIGATORIAMENTE ENTRE ASPAS ("...") os trechos EXATOS que você utilizou do contexto para comprovar sua resposta, acompanhados da localização exata:
   - Para Livros/Compêndio: *"Trecho exato copiado do contexto"* — **[Localização: Nome do Arquivo/Livro, Página X]**
   - Para Artigos Científicos (PubMed/SciELO/Europe PMC): *"Trecho exato copiado do contexto"* — **[Localização: Autores (Ano), Revista, Seção X, Link/DOI]**
   - *Regra de Ouro Bilíngue:* Se o trecho literal original estiver em inglês, mantenha o trecho original entre aspas e adicione logo abaixo: `↳ Tradução técnica: "..."` em português para facilitar a leitura e apresentação no TCC!
"""

def resolve_api_key(provider: str, custom_key: Optional[str] = None) -> str:
    """Obtém a chave de API respeitando custom_key > env > streamlit secrets."""
    if custom_key and custom_key.strip():
        return custom_key.strip()

    env_var = f"{provider.upper()}_API_KEY"
    key = os.getenv(env_var, "").strip()
    if key:
        return key

    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if env_var in st.secrets:
                return str(st.secrets[env_var]).strip()
            elif provider.lower() == "gemini" and "GEMINI_API_KEY" in st.secrets:
                return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    return ""

def generate_answer(
    query: str,
    context_chunks: List[Dict[str, Any]],
    provider: str = "gemini",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gera a resposta clínica fundamentada usando o LLM escolhido com tradução clínica e citações literais entre aspas.
    """
    if not context_chunks:
        return {
            "answer": "⚠️ **Nenhum documento relevante encontrado no acervo.**\n\nPor favor, tente termos clínicos mais diretos ou utilize o modo *Pesquisa Híbrida Ao Vivo*.",
            "sources": []
        }

    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        if chunk.get("doc_type") == "article":
            context_text += (
                f"\n--- [FONTE {i} - ARTIGO CIENTÍFICO ({chunk.get('repo_badge', 'Artigo')})]:\n"
                f"Título: {chunk.get('title', '')}\n"
                f"Autores: {chunk.get('authors', '')} ({chunk.get('year', '')})\n"
                f"Revista: {chunk.get('journal', '')}\n"
                f"DOI: {chunk.get('doi', '')}\n"
                f"Link: {chunk.get('url', '')}\n"
                f"Seção: {chunk.get('page', '')}\n"
                f"Conteúdo:\n{chunk['text']}\n"
            )
        else:
            context_text += (
                f"\n--- [FONTE {i} - COMPÊNDIO CLÍNICO / LIVRO-TEXTO]:\n"
                f"Arquivo: {chunk.get('source', '')} | Referência: {chunk.get('authors', '')} | Página: {chunk.get('page', '')}\n"
                f"Conteúdo:\n{chunk['text']}\n"
            )

    user_prompt = f"""PERGUNTA CLÍNICA DO DENTISTA/ESTUDANTE:
{query}

FRAGMENTOS DA LITERATURA DE ODONTOLOGIA (LIVROS-TEXTO E ARTIGOS CIENTÍFICOS):
{context_text}

Instrução: Sintetize e traduza todo o conhecimento aplicável dos fragmentos acima para responder com precisão máxima à pergunta em português, estruturando nas 3 seções obrigatórias ('### 🩺 Conduta Clínica / Resposta Direta', '### 📚 Fundamentação Científica e Nível de Evidência' e '### 📝 Trechos Literais Utilizados (Comprovação Textual)')."""

    # 1. Provedor Google Gemini (com fallback inteligente de modelos)
    if provider.lower() == "gemini":
        key = resolve_api_key("gemini", api_key)
        if not key:
            return {
                "answer": "⚠️ **Chave de API do Gemini não configurada.**\n\nInsira sua chave gratuita do Google AI Studio na barra lateral para gerar a resposta clínica automática.",
                "sources": context_chunks
            }

        models_to_try = []
        if model_name:
            models_to_try.append(model_name)
        models_to_try.extend([
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-2.5-flash-lite"
        ])
        models_to_try = list(dict.fromkeys(models_to_try))

        last_error = None

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=ODONTO_SYSTEM_PROMPT,
                            temperature=0.15
                        )
                    )
                    if response and response.text:
                        increment_usage()
                        return {
                            "answer": response.text,
                            "sources": context_chunks,
                            "model_used": m
                        }
                except Exception as err:
                    last_error = err
                    continue
        except Exception as err:
            last_error = err

        return {
            "answer": f"❌ Erro ao conectar com o Google Gemini.\n\nDetalhes do erro: `{str(last_error)}`\n\n**Dica:** Verifique se a sua chave no [Google AI Studio](https://aistudio.google.com/app/apikey) está ativa.",
            "sources": context_chunks
        }

    # 2. Provedor OpenAI
    elif provider.lower() == "openai":
        key = resolve_api_key("openai", api_key)
        if not key:
            return {
                "answer": "⚠️ **Chave de API da OpenAI não configurada.**\n\nInsira sua chave na barra lateral.",
                "sources": context_chunks
            }

        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            model_to_use = model_name or "gpt-4o-mini"
            completion = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": ODONTO_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.15
            )
            increment_usage()
            return {
                "answer": completion.choices[0].message.content,
                "sources": context_chunks,
                "model_used": model_to_use
            }
        except Exception as e:
            return {
                "answer": f"❌ Erro ao conectar com a OpenAI: {str(e)}",
                "sources": context_chunks
            }

    # 3. Provedor Groq
    elif provider.lower() == "groq":
        key = resolve_api_key("groq", api_key)
        if not key:
            return {
                "answer": "⚠️ **Chave de API da Groq não configurada.**\n\nInsira sua chave gratuita da Groq na barra lateral.",
                "sources": context_chunks
            }
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=key
            )
            model_to_use = model_name or "llama-3.3-70b-versatile"
            completion = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": ODONTO_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.15
            )
            increment_usage()
            return {
                "answer": completion.choices[0].message.content,
                "sources": context_chunks,
                "model_used": model_to_use
            }
        except Exception as e:
            return {
                "answer": f"❌ Erro ao conectar com a Groq: {str(e)}",
                "sources": context_chunks
            }

    return {
        "answer": f"Provedor '{provider}' não suportado.",
        "sources": context_chunks
    }
