import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import OdontoRAG, DOCUMENTS_PATH
from llm_service import generate_answer, resolve_api_key
from academic_search_service import AcademicSearchService
from usage_tracker import get_today_usage

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página estilo Google Gemini
st.set_page_config(
    page_title="OdontoMind — Inteligência Clínica Baseada em Evidências",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# INJEÇÃO DE CSS ESTILO GEMINI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Tipografia global moderna */
html, body, [class*="css"] {
    font-family: 'Plus+Jakarta+Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Esconde elementos padrão redundantes do Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Título estilo Gemini com gradiente colorido */
.gemini-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #1A73E8 0%, #8E24AA 50%, #D81B60 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
    display: inline-block;
}

.gemini-subtitle {
    font-size: 1.1rem;
    color: #9aa0a6;
    margin-bottom: 1.5rem;
    font-weight: 400;
}

/* Barra de Seleção de Modelo/Modo estilo Pílulas do Gemini */
.selector-container {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 8px 16px;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}

/* Cards de Sugestões de Perguntas Rápidas */
.prompt-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 14px 18px;
    transition: all 0.2s ease;
    cursor: pointer;
    min-height: 85px;
}

.prompt-card:hover {
    background: rgba(255, 255, 255, 0.07);
    border-color: rgba(66, 133, 244, 0.4);
    transform: translateY(-2px);
}

/* Estilo para citações de fontes */
.source-box {
    border-left: 3px solid #1A73E8;
    background: rgba(26, 115, 232, 0.05);
    padding: 10px 14px;
    border-radius: 0 10px 10px 0;
    margin: 8px 0;
}

/* Disclaimer no rodapé estilo Gemini */
.gemini-disclaimer {
    text-align: center;
    color: #80868b;
    font-size: 0.75rem;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Inicializa os serviços
@st.cache_resource
def get_rag_engine():
    return OdontoRAG()

@st.cache_resource
def get_academic_service():
    return AcademicSearchService()

rag = get_rag_engine()
academic = get_academic_service()

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []

# ==============================================================================
# BARRA LATERAL (SIDEBAR — ACERVO & CONFIGURAÇÕES AVANÇADAS)
# ==============================================================================
with st.sidebar:
    st.markdown("### ✨ OdontoMind")
    st.caption("Odontologia Baseada em Evidências")
    st.divider()

    # Status da Chave Oficial (Nunca exibe o valor secreto)
    has_system_key = bool(resolve_api_key("gemini"))
    if has_system_key:
        st.success("🟢 Chave padrão do sistema ativa")
    else:
        st.warning("⚠️ Nenhuma chave padrão detectada")

    # Substituição por chave pessoal
    custom_key_input = st.text_input(
        "Substituir por chave pessoal (opcional):",
        value="",
        type="password",
        placeholder="Cole sua chave aqui...",
        help="Deixe em branco para usar a chave padrão do sistema."
    )
    active_key = custom_key_input if custom_key_input.strip() else None
    if active_key:
        st.caption("🔑 Utilizando sua chave personalizada para esta sessão.")

    st.divider()

    # Monitor de Consumo de Cota Diária
    usage = get_today_usage()
    used_today = usage.get("requests_today", 0)
    daily_limit = usage.get("daily_limit", 1500)
    rpm_limit = usage.get("rpm_limit", 15)
    remaining = max(0, daily_limit - used_today)
    progress_val = min(1.0, used_today / daily_limit)

    st.subheader("📈 Limite de Uso da IA")
    st.progress(progress_val)
    st.caption(f"**Consultas realizadas hoje:** `{used_today}` / `{daily_limit}`")
    st.caption(f"**Restantes hoje:** `{remaining}` consultas")
    st.caption(f"⚡ **Capacidade:** até {rpm_limit} requisições/min")

    st.divider()

    # Gestão do Acervo Local
    stats = rag.get_stats()
    st.subheader("📚 Seu Acervo Permanente")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric(label="PDFs / Livros", value=stats["total_files"])
    with col_s2:
        st.metric(label="Artigos Salvos", value=stats["total_articles"])

    uploaded_files = st.file_uploader(
        "Adicionar livros em PDF (ex: Malamed, Neville):",
        type=["pdf"],
        accept_multiple_files=True
    )
    if uploaded_files:
        if st.button("📥 Indexar PDFs no Acervo", type="primary", use_container_width=True):
            total_added = 0
            pbar = st.progress(0)
            for idx, uploaded_file in enumerate(uploaded_files):
                save_path = os.path.join(DOCUMENTS_PATH, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                count = rag.add_pdf(save_path)
                total_added += count
                pbar.progress((idx + 1) / len(uploaded_files))
            st.success(f"{len(uploaded_files)} PDF(s) indexado(s) com sucesso!")
            st.rerun()

    if stats["total_chunks"] > 0:
        if st.button("🗑️ Limpar Acervo Local", use_container_width=True):
            rag.clear_database()
            st.session_state.search_results = []
            st.warning("Acervo limpo!")
            st.rerun()

    st.divider()
    with st.expander("🎓 Ficha Técnica para o TCC"):
        st.markdown("""
        **Nome do Sistema:** OdontoMind  
        **Classificação:** Agente de Suporte à Decisão Clínica (*Agentic RAG*)  
        **Bases Integradas:** PubMed Central (EUA), SciELO Brasil, Europe PMC  
        **Arquitetura:** Ingestão de texto completo em XML/JSON com fatiamento vetorial local e citações literais.
        """)

# ==============================================================================
# ÁREA PRINCIPAL DO CHAT ESTILO GOOGLE GEMINI
# ==============================================================================

# Cabeçalho Superior Minimalista
col_h1, col_h2 = st.columns([8, 2])
with col_h1:
    st.markdown('<div class="gemini-title">OdontoMind ✨</div>', unsafe_allow_html=True)
    st.markdown('<div class="gemini-subtitle">Inteligência Artificial Clínica e Científica para Odontologia</div>', unsafe_allow_html=True)

# BARRA DE SELEÇÃO DE MODELO E MODO DIRETO NO CHAT (Estilo Gemini)
col_mode, col_model, col_repo = st.columns([4, 3, 3])

with col_mode:
    mode_option = st.selectbox(
        "Modo de Operação:",
        options=[
            ("🌐 Pesquisa Ao Vivo (Multi-Bases Mundiais & Nacionais)", "live"),
            ("📚 Meu Acervo Curado (Livros & PDFs Salvos)", "acervo")
        ],
        format_func=lambda x: x[0],
        index=0,
        help="Escolha se a IA deve buscar artigos em tempo real na literatura mundial ou consultar apenas seus livros locais."
    )[1]

with col_model:
    model_choice = st.selectbox(
        "Modelo de IA:",
        options=[
            ("⚡ Gemini 3.5 Flash-Lite (Ultrarrápido)", "gemini-3.5-flash-lite"),
            ("🧠 Gemini 3.8 Flash (Mais Profundo)", "gemini-3.8-flash")
        ],
        format_func=lambda x: x[0],
        index=0,
        help="Selecione o motor generativo do Gemini para formular a resposta."
    )[1]

with col_repo:
    if mode_option == "live":
        repo_choice = st.selectbox(
            "Bases Ativas:",
            options=[
                ("🌐 Todas (PubMed + SciELO + Europe PMC)", "all"),
                ("🇧🇷 SciELO Brasil (USP, UNESP, SBPqO)", "scielo"),
                ("🇺🇸 PubMed Central (EUA)", "pubmed"),
                ("🇪🇺 Europe PMC (Europa / Cochrane)", "europe_pmc")
            ],
            format_func=lambda x: x[0],
            index=0
        )[1]
    else:
        st.selectbox("Base Ativa:", options=["📘 Acervo Fechado (Malamed, Livros)"], disabled=True)
        repo_choice = "acervo"

st.divider()

# SEÇÃO DE BOAS-VINDAS E SUGESTÕES RÁPIDAS (Quando não há mensagens ainda)
quick_prompt = None

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="font-weight: 600; font-size: 1.8rem; margin-bottom: 0.3rem;">Olá, Doutor(a).</h2>
        <p style="color: #9aa0a6; font-size: 1.15rem;">O que vamos pesquisar na literatura odontológica hoje?</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💉 Dose máxima de Lidocaína (Malamed)\n\nCálculo de mg/kg e teto por peso corporal", use_container_width=True):
            quick_prompt = "Qual a dose máxima recomendada de lidocaína 2% com epinefrina 1:100.000 para um adulto hígido segundo a literatura de anestesiologia odontológica?"
        if st.button("❤️ Profilaxia para Endocardite (AHA/CFO)\n\nPacientes de alto risco e protocolos antibióticos", use_container_width=True):
            quick_prompt = "Qual o protocolo atual de profilaxia antibiótica para prevenção de endocardite infecciosa em procedimentos odontológicos e quais pacientes têm indicação formal?"

    with col2:
        if st.button("🤰 Anestesia local em Gestantes\n\nCondutas por trimestre, riscos e contraindicações", use_container_width=True):
            quick_prompt = "Quais são as condutas e anestésicos locais de escolha para atendimento de gestantes na clínica odontológica?"
        if st.button("🔬 Clorexidina na Mucosite Peri-implantar\n\nEvidências recentes de ensaios clínicos randomizados", use_container_width=True):
            quick_prompt = "Qual a eficácia clínica da clorexidina no manejo da mucosite peri-implantar segundo os ensaios clínicos mais recentes?"

    st.markdown("<br>", unsafe_allow_html=True)

# EXIBIÇÃO DO HISTÓRICO DE MENSAGENS (ESTILO GEMINI)
for msg in st.session_state.messages:
    avatar_icon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])
        
        # Badges informativos no rodapé da mensagem
        caption_items = []
        if msg.get("mode"):
            caption_items.append(f"Modo: `{msg['mode']}`")
        if msg.get("model_used"):
            caption_items.append(f"Modelo: `{msg['model_used']}`")
        if msg.get("keywords"):
            caption_items.append(f"Termos: `{msg['keywords']}`")
        
        if caption_items:
            st.caption(" • ".join(caption_items))

        # Drawer expansível de evidências consultadas
        if msg.get("sources"):
            with st.expander(f"📖 Evidências e Fontes Consultadas ({len(msg['sources'])} trechos)"):
                for idx, src in enumerate(msg["sources"], 1):
                    badge = src.get("repo_badge", "📘 Livro/Manual")
                    if src.get("doc_type") == "article":
                        st.markdown(f"""
                        **[Fonte {idx}] {badge}**  
                        📄 **Título:** [{src.get('title')}]({src.get('url')})  
                        ✍️ **Autores:** {src.get('authors')} ({src.get('year')}) — *{src.get('journal')}*  
                        🔗 **DOI / Link:** [{src.get('doi') or src.get('url')}]({src.get('url')}) | **Seção:** `{src.get('page')}`  
                        > {src['text']}
                        """)
                    else:
                        st.markdown(f"""
                        **[Fonte {idx}] {badge}** `Arquivo: {src['source']}` — **Página {src['page']}**
                        > {src['text']}
                        """)

# CAMPO DE ENTRADA DO CHAT (FLUTUANTE ESTILO GEMINI)
user_query = st.chat_input("Pergunte ao OdontoMind sobre condutas, farmacologia ou artigos científicos...")
if quick_prompt:
    user_query = quick_prompt

if user_query:
    # 1. Registra e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    # 2. Processamento do Agente OdontoMind
    with st.chat_message("assistant", avatar="✨"):
        keywords_used = None
        sources_found = []
        mode_label = "Ao Vivo (Multi-Bases)" if mode_option == "live" else "Acervo Curado (Livros)"

        # MODO 1: PESQUISA MULTI-BASES AO VIVO
        if mode_option == "live":
            with st.spinner("1/2 Vasculhando simultaneamente PubMed, SciELO Brasil e Europe PMC..."):
                search_data = academic.live_multi_search_and_prepare_context(
                    question=user_query,
                    source_filter=repo_choice,
                    api_key=active_key,
                    max_articles=4
                )
                keywords_used = search_data.get("keywords")
                articles_found = search_data.get("articles", [])
                sources_found = search_data.get("chunks", [])

            if not sources_found:
                answer = "⚠️ **Nenhum artigo de acesso aberto com alto nível de evidência foi localizado nas bases para essa busca.**\n\nTente reformular com outros termos ou mude para o modo *Meu Acervo Curado*."
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": [],
                    "keywords": keywords_used,
                    "mode": mode_label
                })
            else:
                with st.spinner(f"2/2 Sintetizando evidências com citações exatas ({len(articles_found)} artigos consultados)..."):
                    response_data = generate_answer(
                        query=user_query,
                        context_chunks=sources_found,
                        provider="gemini",
                        api_key=active_key,
                        model_name=model_choice
                    )

                st.markdown(response_data["answer"])

                caption_items = [f"Modo: `{mode_label}`", f"Modelo: `{response_data.get('model_used', model_choice)}`"]
                if keywords_used:
                    caption_items.append(f"Termos: `{keywords_used}`")
                st.caption(" • ".join(caption_items))

                with st.expander(f"📖 Evidências e Fontes Consultadas ({len(sources_found)} trechos)"):
                    for idx, src in enumerate(sources_found, 1):
                        st.markdown(f"""
                        **[Artigo {idx}] {src.get('repo_badge', '')}**  
                        📄 **Título:** [{src.get('title')}]({src.get('url')})  
                        ✍️ **Autores:** {src.get('authors')} ({src.get('year')}) — *{src.get('journal')}*  
                        🔗 **DOI / Link:** [{src.get('doi') or src.get('url')}]({src.get('url')}) | **Seção:** `{src.get('page')}`  
                        > {src['text']}
                        """)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["answer"],
                    "sources": sources_found,
                    "keywords": keywords_used,
                    "mode": mode_label,
                    "model_used": response_data.get("model_used")
                })

        # MODO 2: ACERVO CURADO FECHADO
        else:
            with st.spinner("Pesquisando estritamente nos PDFs e livros do seu acervo..."):
                sources_found = rag.search_relevant_excerpts(user_query, top_k=4)
                response_data = generate_answer(
                    query=user_query,
                    context_chunks=sources_found,
                    provider="gemini",
                    api_key=active_key,
                    model_name=model_choice
                )

            st.markdown(response_data["answer"])
            st.caption(f"Modo: `{mode_label}` • Modelo: `{response_data.get('model_used', model_choice)}`")

            if sources_found:
                with st.expander(f"📖 Trechos Consultados do Seu Acervo ({len(sources_found)} fontes)"):
                    for idx, src in enumerate(sources_found, 1):
                        st.markdown(f"""
                        **[Fonte {idx} - Livro/Manual]** `Arquivo: {src['source']}` — **Página {src['page']}**
                        > {src['text']}
                        """)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["answer"],
                "sources": sources_found,
                "mode": mode_label,
                "model_used": response_data.get("model_used")
            })

# Disclaimer discreto no rodapé estilo Gemini
st.markdown('<div class="gemini-disclaimer">OdontoMind é um assistente acadêmico para Odontologia Baseada em Evidências. Sempre verifique as fontes primárias citadas antes de tomar condutas clínicas.</div>', unsafe_allow_html=True)
