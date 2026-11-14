import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env automaticamente
load_dotenv()

# Garante o uso dos certificados SSL do Windows para evitar erros de conexão
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

ODONTO_SYSTEM_PROMPT = """Você é a OdontoIA, uma assistente de inteligência artificial de alta precisão clínica voltada exclusivamente para Odontologia Baseada em Evidências (OBE).
Sua missão é responder às dúvidas clínicas de estudantes e cirurgiões-dentistas com base ESTRITAMENTE nos fragmentos de literatura científica, artigos e livros fornecidos no contexto.

DIRETRIZES FUNDAMENTAIS DE SEGURANÇA E CONDUTA CLÍNICA:
1. NUNCA INVENTE informações, dosagens, contraindicações ou protocolos.
2. Se a informação necessária NÃO constar de forma clara no contexto fornecido, declare explicitamente:
   "⚠️ Esta informação não foi encontrada no acervo bibliográfico indexado. Por segurança clínica, consulte a literatura de referência antes de tomar qualquer conduta."
3. ESTRUTURAÇÃO OBRIGATÓRIA DA RESPOSTA:
   Toda resposta deve seguir RIGOROSAMENTE as 3 seções abaixo:

   ### 🩺 Conduta Clínica / Resposta Direta
   Explique a resposta de forma clara, didática, profissional e objetiva.

   ### 📚 Fundamentação e Nível de Evidência
   Explique os mecanismos, justificativas científicas, pontos de atenção ou contraindicações citando os autores, obras e revistas.

   ### 📝 Trechos Literais Utilizados (Comprovação Textual)
   Transcreva OBRIGATORIAMENTE ENTRE ASPAS ("...") os trechos EXATOS que você utilizou do texto para comprovar sua resposta, acompanhados da localização exata de onde cada um foi retirado:
   - Para Livros/Manuais: *"Trecho exato copiado do contexto"* — **[Localização: Nome do Arquivo/Livro, Página X]**
   - Para Artigos PubMed: *"Trecho exato copiado do contexto"* — **[Localização: Autores (Ano), Revista, Seção X, Link/DOI]**

4. Fidelidade Absoluta: Não altere o texto dentro das aspas. Ele deve ser a cópia literal dos dados que constam no contexto.
"""

def generate_answer(
    query: str,
    context_chunks: List[Dict[str, Any]],
    provider: str = "gemini",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gera a resposta clínica fundamentada usando o LLM escolhido com citações literais entre aspas.
    """
    if not context_chunks:
        return {
            "answer": "⚠️ **Nenhum documento relevante encontrado no acervo.**\n\nPor favor, adicione artigos pelo buscador do PubMed ou faça upload de livros em PDF na barra lateral para que a IA possa fundamentar a resposta.",
            "sources": []
        }

    # Monta o contexto textual distinguindo livros e artigos científicos do PubMed
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        if chunk.get("doc_type") == "article":
            context_text += (
                f"\n--- [FONTE {i} - ARTIGO CIENTÍFICO PUBMED]:\n"
                f"Título: {chunk.get('title', '')}\n"
                f"Autores: {chunk.get('authors', '')} ({chunk.get('year', '')})\n"
                f"Revista: {chunk.get('journal', '')}\n"
                f"DOI: {chunk.get('doi', '')}\n"
                f"Link PubMed: {chunk.get('url', '')}\n"
                f"Seção: {chunk.get('page', '')}\n"
                f"Conteúdo:\n{chunk['text']}\n"
            )
        else:
            context_text += (
                f"\n--- [FONTE {i} - LIVRO/MANUAL]:\n"
                f"Arquivo: {chunk.get('source', '')} | Página: {chunk.get('page', '')}\n"
                f"Conteúdo:\n{chunk['text']}\n"
            )

    user_prompt = f"""PERGUNTA CLÍNICA DO DENTISTA/ESTUDANTE:
{query}

FRAGMENTOS DA LITERATURA DE ODONTOLOGIA EXTRAÍDOS DO SEU ACERVO:
{context_text}

Instrução: Responda à pergunta seguindo estritamente a estrutura solicitada no sistema, incluindo OBRIGATORIAMENTE a seção '### 📝 Trechos Literais Utilizados (Comprovação Textual)' com os fragmentos exatos ENTRE ASPAS ("...") e suas respectivas localizações (arquivo, página, seção e link)."""

    # 1. Provedor Google Gemini (com fallback inteligente de modelos)
    if provider.lower() == "gemini":
        key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        if not key:
            return {
                "answer": "⚠️ **Chave de API do Gemini não configurada.**\n\nInsira sua chave gratuita do Google AI Studio na barra lateral para gerar a resposta clínica automática.",
                "sources": context_chunks
            }

        # Modelos mais modernos e com alta disponibilidade na API
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
        # Remove duplicatas preservando ordem
        models_to_try = list(dict.fromkeys(models_to_try))

        last_error = None

        # Tentativa com o SDK oficial moderno `google-genai`
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
                            temperature=0.1
                        )
                    )
                    if response and response.text:
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
        key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
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
                temperature=0.1
            )
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
        key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
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
                temperature=0.1
            )
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
