import os
import datetime
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

html, body, [class*="css"] {
    font-family: 'Plus+Jakarta+Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Título estilo Gemini com gradiente colorido */
.gemini-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #1A73E8 0%, #8E24AA 50%, #D81B60 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.1rem;
    display: inline-block;
}

.gemini-subtitle {
    font-size: 1.05rem;
    color: #9aa0a6;
    margin-bottom: 1.2rem;
    font-weight: 400;
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

.gemini-disclaimer {
    text-align: center;
    color: #80868b;
    font-size: 0.75rem;
    margin-top: 1.5rem;
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
# BARRA LATERAL (SIDEBAR — MONITOR DE COTA & CONFIGURAÇÕES)
# ==============================================================================
with st.sidebar:
    st.markdown("### ✨ OdontoMind")
    st.caption("Odontologia Baseada em Evidências (Arquitetura ECC Hybrid RAG)")
    st.divider()

    # Status da Chave Oficial
    has_system_key = bool(resolve_api_key("gemini"))
    if has_system_key:
        st.success("🟢 Chave padrão do sistema ativa")
    else:
        st.warning("⚠️ Nenhuma chave padrão detectada")

    # Substituição por chave pessoal opcional
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

    # Resumo do Acervo
    stats = rag.get_stats()
    st.subheader("📊 Seu Acervo Permanente")
    st.metric(label="Trechos Clínicos Mapeados", value=stats["total_chunks"])
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric(label="PDFs / Livros", value=stats["total_files"])
    with col_s2:
        st.metric(label="Artigos Salvos", value=stats["total_articles"])

    if stats["total_chunks"] > 0:
        if st.button("🔄 Restaurar Acervo Padrão-Ouro", use_container_width=True):
            rag.clear_database()
            st.session_state.search_results = []
            st.success("Acervo restaurado para o Compêndio Clínico Padrão-Ouro!")
            st.rerun()

    st.divider()
    with st.expander("🎓 Ficha Técnica para o TCC"):
        st.markdown("""
        **Nome do Sistema:** OdontoMind  
        **Classificação:** Agente Híbrido de Suporte à Decisão Clínica (*Hybrid Agentic RAG — Metodologia ECC*)  
        **Bases Científicas Ao Vivo:** PubMed Central (EUA), SciELO Brasil (OpenAlex), Europe PMC  
        **Compêndio Padrão-Ouro Integrado:** Malamed (Anestesia), Hupp/Peterson (Cirurgia/Exodontia), Andrade & AHA/CFO (Farmacologia), Cohen/Lopes & Siqueira (Endodontia), Lindhe (Periodontia), Baratieri (Dentística), Neville (Patologia Oral).
        """)

# ==============================================================================
# CABEÇALHO SUPERIOR
# ==============================================================================
col_head1, col_head2 = st.columns([8, 2])
with col_head1:
    st.markdown('<div class="gemini-title">OdontoMind ✨</div>', unsafe_allow_html=True)
    st.markdown('<div class="gemini-subtitle">Agente Híbrido de Odontologia Baseada em Evidências (PubMed, SciELO Brasil, Europe PMC e Compêndio Clínico)</div>', unsafe_allow_html=True)
with col_head2:
    if len(st.session_state.messages) > 0:
        if st.button("➕ Nova Conversa", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# NAVEGAÇÃO PRINCIPAL (ESTILO GEMINI MODERNO)
nav_chat, nav_coletor, nav_livros = st.tabs([
    "💬 Chat Clínico OdontoMind",
    "🔬 Coletor & Biblioteca de Artigos (Pesquisar e Salvar)",
    "📂 Livros e Compêndio em PDF"
])

# ==============================================================================
# ABA 1: CHAT CLÍNICO
# ==============================================================================
with nav_chat:
    # BARRA DE SELEÇÃO DE MODELO E MODO DIRETO NO CHAT
    col_mode, col_model, col_repo = st.columns([4, 3, 3])

    with col_mode:
        mode_option = st.selectbox(
            "Modo de Operação:",
            options=[
                ("🌐 Pesquisa Híbrida Ao Vivo (Multi-Bases + Compêndio Clínico)", "live"),
                ("📚 Apenas Meu Acervo Curado (Compêndio, Livros & Artigos Salvos)", "acervo")
            ],
            format_func=lambda x: x[0],
            index=0,
            help="No Modo Híbrido Ao Vivo, o agente combina os protocolos clássicos dos livros (Hupp, Malamed, Cohen, Lindhe) com artigos científicos buscados em tempo real no PubMed, SciELO e Europe PMC."
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
                    ("🌐 Todas (PubMed + SciELO + Europe PMC + Compêndio)", "all"),
                    ("🇧🇷 SciELO Brasil + Compêndio Clínico", "scielo"),
                    ("🇺🇸 PubMed Central (EUA) + Compêndio Clínico", "pubmed"),
                    ("🇪🇺 Europe PMC (Europa) + Compêndio Clínico", "europe_pmc")
                ],
                format_func=lambda x: x[0],
                index=0
            )[1]
        else:
            st.selectbox("Base Ativa:", options=["📘 Acervo Fechado (Compêndio Clínico, Livros e Artigos Salvos)"], disabled=True)
            repo_choice = "acervo"

    st.divider()

    # SEÇÃO DE BOAS-VINDAS E SUGESTÕES RÁPIDAS
    quick_prompt = None

    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style="margin: 1.2rem 0 1.2rem 0;">
            <h2 style="font-weight: 600; font-size: 1.7rem; margin-bottom: 0.2rem;">Olá, Doutor(a).</h2>
            <p style="color: #9aa0a6; font-size: 1.08rem;">O que vamos pesquisar na literatura odontológica hoje?</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🦷 Extração de Dentes Posteriores\n\nPasso a passo cirúrgico, alavancas e fórceps (Hupp/Peterson)", use_container_width=True):
                quick_prompt = "Qual o passo a passo de uma extração de dentes posteriores, incluindo anestesia, sindesmotomia, alavancas, escolha dos fórceps e sutura?"
            if st.button("💉 Dose máxima de Lidocaína (Malamed)\n\nCálculo de mg/kg e limite de tubetes em adultos e cardiopatas", use_container_width=True):
                quick_prompt = "Qual a dose máxima recomendada de lidocaína 2% com epinefrina 1:100.000 para um adulto hígido e para um paciente cardiopata segundo Malamed?"

        with col2:
            if st.button("🔬 Passo a Passo Endodontia (Cohen)\n\nAbertura, odontometria, irrigação NaOCl/EDTA e obturação", use_container_width=True):
                quick_prompt = "Qual o passo a passo completo do tratamento endodôntico (canal), incluindo soluções irrigadoras, odontometria e remoção de smear layer?"
            if st.button("❤️ Profilaxia para Endocardite (AHA/CFO)\n\nPacientes de alto risco e posologia para alérgicos", use_container_width=True):
                quick_prompt = "Qual o protocolo atual de profilaxia antibiótica para prevenção de endocardite infecciosa em procedimentos odontológicos e quais pacientes têm indicação formal?"

        with col3:
            if st.button("🤰 Atendimento a Gestantes\n\nTrimestre ideal, anestésico de escolha e fármacos seguros", use_container_width=True):
                quick_prompt = "Quais são as condutas, anestésicos locais de escolha e medicamentos seguros ou contraindicados para atendimento de gestantes na odontologia?"
            if st.button("🪥 Curetas Gracey e Periodontia (Lindhe)\n\nNumeração específica por face dentária e estágios", use_container_width=True):
                quick_prompt = "Qual o passo a passo da raspagem periodontal, a numeração específica das curetas de Gracey para cada região e a classificação da periodontite?"

        st.markdown("<br>", unsafe_allow_html=True)

    # HISTÓRICO DE MENSAGENS
    for msg in st.session_state.messages:
        avatar_icon = "👤" if msg["role"] == "user" else "✨"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

            caption_items = []
            if msg.get("mode"):
                caption_items.append(f"Modo: `{msg['mode']}`")
            if msg.get("intent"):
                caption_items.append(f"Intenção: `{msg['intent']}`")
            if msg.get("model_used"):
                caption_items.append(f"Modelo: `{msg['model_used']}`")
            if msg.get("keywords"):
                caption_items.append(f"Descritores: `{msg['keywords']}`")
            if caption_items:
                st.caption(" • ".join(caption_items))

            if msg.get("sources"):
                with st.expander(f"📖 Evidências e Fontes Consultadas ({len(msg['sources'])} trechos)"):
                    for idx, src in enumerate(msg["sources"], 1):
                        badge = src.get("repo_badge", "📘 Compêndio/Livro")
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
                            **[Fonte {idx}] {badge}** `Arquivo: {src['source']}` — **Página {src['page']}** ({src.get('authors', 'Referência Clássica')})  
                            > {src['text']}
                            """)

    # INPUT DO CHAT
    user_query = st.chat_input("Pergunte ao OdontoMind sobre passo a passo cirúrgico, condutas, farmacologia ou artigos...")
    if quick_prompt:
        user_query = quick_prompt

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        with st.chat_message("assistant", avatar="✨"):
            keywords_used = None
            intent_detected = None
            sources_found = []
            mode_label = "Híbrido Ao Vivo (Multi-Bases + Compêndio)" if mode_option == "live" else "Acervo Curado (Compêndio & Livros)"

            if mode_option == "live":
                with st.spinner("1/2 Executando busca híbrida ECC (PubMed, SciELO Brasil, Europe PMC + Compêndio Clínico)..."):
                    search_data = academic.live_multi_search_and_prepare_context(
                        question=user_query,
                        source_filter=repo_choice,
                        api_key=active_key,
                        max_articles=5,
                        local_rag=rag
                    )
                    keywords_used = search_data.get("keywords")
                    intent_detected = search_data.get("intent")
                    articles_found = search_data.get("articles", [])
                    sources_found = search_data.get("chunks", [])

                if not sources_found:
                    # Fallback garantido para o Compêndio Clínico Local
                    sources_found = rag.search_relevant_excerpts(user_query, top_k=4)

                with st.spinner(f"2/2 Traduzindo e sintetizando evidências com citações literais ({len(sources_found)} trechos de alta relevância)..."):
                    response_data = generate_answer(
                        query=user_query,
                        context_chunks=sources_found,
                        provider="gemini",
                        api_key=active_key,
                        model_name=model_choice
                    )

                st.markdown(response_data["answer"])

                caption_items = [f"Modo: `{mode_label}`"]
                if intent_detected:
                    caption_items.append(f"Intenção: `{intent_detected}`")
                caption_items.append(f"Modelo: `{response_data.get('model_used', model_choice)}`")
                if keywords_used:
                    caption_items.append(f"Descritores: `{keywords_used}`")
                st.caption(" • ".join(caption_items))

                with st.expander(f"📖 Evidências e Fontes Consultadas ({len(sources_found)} trechos)"):
                    for idx, src in enumerate(sources_found, 1):
                        badge = src.get("repo_badge", "📘 Compêndio/Livro")
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
                            **[Fonte {idx}] {badge}** `Arquivo: {src['source']}` — **Página {src['page']}** ({src.get('authors', 'Referência Clássica')})  
                            > {src['text']}
                            """)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["answer"],
                    "sources": sources_found,
                    "keywords": keywords_used,
                    "intent": intent_detected,
                    "mode": mode_label,
                    "model_used": response_data.get("model_used")
                })

            else:
                with st.spinner("Pesquisando com busca híbrida (vetorial + sinônimos clínicos) no seu acervo..."):
                    sources_found = rag.search_relevant_excerpts(user_query, top_k=5)
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
                            if src.get("doc_type") == "article":
                                st.markdown(f"""
                                **[Fonte {idx} - Artigo do Acervo]**  
                                📄 **Título:** [{src.get('title')}]({src.get('url')})  
                                ✍️ **Autores:** {src.get('authors')} ({src.get('year')}) — *{src.get('journal')}*  
                                🔗 **DOI / Link:** [{src.get('doi') or src.get('url')}]({src.get('url')}) | **Seção:** `{src.get('page')}`  
                                > {src['text']}
                                """)
                            else:
                                st.markdown(f"""
                                **[Fonte {idx} - Livro/Compêndio]** `Arquivo: {src['source']}` — **Página {src['page']}** ({src.get('authors', 'Referência Clássica')})  
                                > {src['text']}
                                """)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["answer"],
                    "sources": sources_found,
                    "mode": mode_label,
                    "model_used": response_data.get("model_used")
                })

    st.markdown('<div class="gemini-disclaimer">OdontoMind é um Agente de Suporte à Decisão Clínica para Odontologia Baseada em Evidências. Sempre valide as condutas com as fontes primárias citadas.</div>', unsafe_allow_html=True)

# ==============================================================================
# ABA 2: COLETOR E BIBLIOTECA DE ARTIGOS (PESQUISAR & SALVAR)
# ==============================================================================
with nav_coletor:
    st.markdown("### 🔬 Coletor de Artigos Científicos (Pesquisar & Salvar no Acervo)")
    st.write("Pesquise temas clínicos para encontrar artigos de alto nível de evidência e **salvá-los permanentemente no seu acervo** para consulta no modo fechado.")

    col_cq, col_crep, col_cnum = st.columns([4, 3, 2])
    with col_cq:
        coletor_query = st.text_input(
            "Pesquisar Tema para Salvar:",
            placeholder="Ex: exodontia dentes posteriores, peri-implantite tratamento, clareamento caseiro vs consultorio"
        )
    with col_crep:
        coletor_repo = st.selectbox(
            "Base de Busca:",
            options=[
                ("🌐 Todas as Bases", "all"),
                ("🇧🇷 SciELO Brasil (USP, UNICAMP)", "scielo"),
                ("🇺🇸 PubMed Central (EUA)", "pubmed"),
                ("🇪🇺 Europe PMC (Europa)", "europe_pmc")
            ],
            format_func=lambda x: x[0]
        )[1]
    with col_cnum:
        coletor_max = st.selectbox("Artigos por Base:", options=[2, 3, 5], index=1)

    if st.button("🔍 Pesquisar Artigos para Salvar", type="primary"):
        if not coletor_query.strip():
            st.warning("Por favor, digite um tema para pesquisar.")
        else:
            with st.spinner("Buscando nas bases científicas selecionadas com o Planejador ECC..."):
                results = academic.search_all_sources(
                    query=coletor_query,
                    source_filter=coletor_repo,
                    max_per_source=coletor_max,
                    study_type="all_evidence",
                    api_key=active_key
                )
                st.session_state.search_results = results
                if not results:
                    st.warning("Nenhum artigo encontrado. Tente termos sinônimos ou selecione 'Todas as Bases'.")

    # Exibição dos artigos encontrados para salvar
    if st.session_state.search_results:
        st.write(f"#### 📄 Artigos Encontrados ({len(st.session_state.search_results)})")

        if st.button("📥 Salvar TODOS os Artigos Encontrados no Acervo Permanente", use_container_width=True):
            pbar = st.progress(0)
            status_box = st.empty()
            total_indexed = 0
            for i, art in enumerate(st.session_state.search_results):
                status_box.text(f"Salvando: {art['title'][:60]}...")
                chunks = academic.fetch_article_content(art)
                count = rag.add_article(art, chunks)
                total_indexed += count
                pbar.progress((i + 1) / len(st.session_state.search_results))
            status_box.success(f"Concluído! {total_indexed} trechos científicos salvos permanentemente no seu acervo.")
            st.rerun()

        st.divider()

        for i, art in enumerate(st.session_state.search_results):
            with st.container():
                st.markdown(f"##### {i+1}. {art.get('repo_badge', '')} [{art['title']}]({art['url']})")
                st.markdown(f"**Autores:** {art['authors']} | **Revista:** *{art['journal']}* ({art['year']})")
                badge_doi = f"**DOI:** [{art['doi']}](https://doi.org/{art['doi']})" if art.get("doi") else ""
                st.markdown(f"**Origem:** `{art['source_repo']}` | {badge_doi}")

                if st.button(f"📥 Salvar este Artigo no Acervo Permanente", key=f"btn_save_coletor_{art['id']}"):
                    with st.spinner("Extraindo e salvando no banco vetorial..."):
                        chunks = academic.fetch_article_content(art)
                        count = rag.add_article(art, chunks)
                        st.success(f"Artigo salvo com sucesso! ({count} trechos indexados com citação).")
                        st.rerun()
                st.divider()

    # LISTA DE ARTIGOS JÁ SALVOS NO ACERVO
    st.markdown("### 📚 Artigos Atualmente Salvos no Seu Acervo")
    saved_articles = rag.get_indexed_articles()
    if not saved_articles:
        st.info("Nenhum artigo salvo manualmente no seu acervo ainda. Faça uma busca acima para salvar seus primeiros artigos!")
    else:
        st.caption(f"Total de artigos catalogados: **{len(saved_articles)}**")
        for art in saved_articles:
            with st.expander(f"🔬 {art.get('repo_badge', '📄')} {art.get('title')} ({art.get('year')})"):
                st.markdown(f"**Autores:** {art.get('authors')}")
                st.markdown(f"**Revista:** *{art.get('journal')}* | **Trechos Indexados:** `{art.get('chunks_count', '?')}`")
                st.markdown(f"🔗 [Acessar Artigo Original]({art.get('url')})")

# ==============================================================================
# ABA 3: LIVROS E COMPÊNDIO EM PDF
# ==============================================================================
with nav_livros:
    st.markdown("### 📂 Compêndio Clínico Padrão-Ouro & Upload de Livros em PDF")
    st.info("📘 **Compêndio Clínico Integrado Automaticamente:** O OdontoMind já vem com um Compêndio Clínico Padrão-Ouro de 10 páginas cobrindo **Cirurgia/Exodontia (Hupp/Peterson), Anestesiologia (Malamed), Farmacologia/Endocardite (Andrade/AHA/CFO), Endodontia (Cohen/Lopes & Siqueira), Periodontia (Lindhe), Dentística (Baratieri) e Patologia Oral (Neville)**. Você também pode adicionar novos capítulos e livros em PDF abaixo!")

    uploaded_files_main = st.file_uploader(
        "Selecione um ou mais arquivos PDF de livros:",
        type=["pdf"],
        accept_multiple_files=True,
        key="uploader_main"
    )

    if uploaded_files_main:
        if st.button("📥 Processar e Indexar Livros Selecionados", type="primary"):
            pbar = st.progress(0)
            status_box = st.empty()
            total_added = 0
            for idx, uploaded_file in enumerate(uploaded_files_main):
                status_box.text(f"Lendo e mapeando páginas: {uploaded_file.name}...")
                save_path = os.path.join(DOCUMENTS_PATH, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                chunks_count = rag.add_pdf(save_path)
                total_added += chunks_count
                pbar.progress((idx + 1) / len(uploaded_files_main))

            status_box.success(f"Concluído! {len(uploaded_files_main)} arquivo(s) indexado(s) com {total_added} páginas/trechos mapeados.")
            st.rerun()

    st.divider()
    st.subheader(f"📘 Arquivos de Livros Salvos no Acervo ({len(stats['files'])})")
    for f in stats["files"]:
        st.write(f"- 📕 **{f}**")
