import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import OdontoRAG, DOCUMENTS_PATH
from llm_service import generate_answer, resolve_api_key
from academic_search_service import AcademicSearchService
from usage_tracker import get_today_usage

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="OdontoIA — IA Multi-Bases para Odontologia Baseada em Evidências",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa os serviços
@st.cache_resource
def get_rag_engine():
    return OdontoRAG()

@st.cache_resource
def get_academic_service():
    return AcademicSearchService()

rag = get_rag_engine()
academic = get_academic_service()

# 1. Histórico do Chat em Tempo Real (Busca Multi-Bases)
if "messages_live" not in st.session_state:
    st.session_state.messages_live = [
        {
            "role": "assistant",
            "content": "Olá, doutor(a)! Este é o **Modo de Pesquisa Viva Multi-Bases**.\n\nQualquer dúvida clínica que você enviar aqui será pesquisada simultaneamente no **PubMed (EUA)**, **SciELO (Brasil / USP / UNICAMP)** e **Europe PMC (Europa)**.\n\nO que você gostaria de investigar na literatura mundial e nacional hoje?",
            "sources": [],
            "keywords": None
        }
    ]

# 2. Histórico do Chat do Acervo Pessoal (Apenas livros/PDFs curados)
if "messages_acervo" not in st.session_state:
    st.session_state.messages_acervo = [
        {
            "role": "assistant",
            "content": "Olá, doutor(a)! Este é o **Modo Acervo Curado (Base Fechada)**.\n\nMinhas respostas aqui são limitadas **estritamente aos livros, manuais e PDFs que você adicionou** na sua biblioteca pessoal (ex: Malamed, Lindhe, Neville).\n\nQual dúvida você deseja consultar no seu acervo bibliográfico?",
            "sources": []
        }
    ]

if "search_results" not in st.session_state:
    st.session_state.search_results = []

# BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/tooth.png", width=64)
    st.title("🦷 OdontoIA")
    st.caption("Odontologia Baseada em Evidências — Multi-Bases")
    st.divider()

    # 1. Configurações da IA
    st.subheader("⚙️ Configuração do Motor")
    provider = st.selectbox(
        "Provedor:",
        options=["Gemini (Recomendado)", "OpenAI", "Groq"],
        index=0
    )

    provider_map = {
        "Gemini (Recomendado)": "gemini",
        "OpenAI": "openai",
        "Groq": "groq"
    }
    selected_provider = provider_map[provider]

    # Verifica se há chave padrão no servidor (.env ou Streamlit Secrets) sem exibi-la
    has_system_key = bool(resolve_api_key(selected_provider))

    if has_system_key:
        st.success("🟢 Chave padrão ativa no sistema")
    else:
        st.warning("⚠️ Nenhuma chave padrão detectada")

    # Campo opcional para o usuário usar chave própria (NUNCA exibe a chave padrão)
    custom_key_input = st.text_input(
        "Substituir por chave pessoal (opcional):",
        value="",
        type="password",
        placeholder="Cole sua chave aqui se desejar...",
        help="Deixe em branco para usar a chave padrão do sistema sem precisar configurar nada."
    )

    if custom_key_input:
        st.caption("🔑 Utilizando sua chave personalizada para esta sessão.")
        active_key = custom_key_input
    else:
        active_key = None

    st.divider()

    # Monitor de Limite e Consumo Diário (Google Gemini Free Tier)
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
    st.caption(f"⚡ **Capacidade por minuto:** até {rpm_limit} requisições/min")

    st.divider()

    # Filtro de Repositório Padrão
    st.subheader("🌐 Repositórios Científicos Ativos")
    selected_repo = st.radio(
        "Bases de pesquisa ao vivo:",
        options=[
            ("🌐 Todas as Bases (PubMed + SciELO + Europe PMC)", "all"),
            ("🇧🇷 SciELO / Literatura Brasileira (USP, UNESP)", "scielo"),
            ("🇺🇸 PubMed Central (EUA / NLM)", "pubmed"),
            ("🇪🇺 Europe PMC (Europa / Cochrane)", "europe_pmc")
        ],
        format_func=lambda x: x[0],
        index=0
    )[1]

    st.divider()

    # Métricas do Acervo
    stats = rag.get_stats()
    st.subheader("📊 Seu Acervo Local")
    st.metric(label="Trechos Clínicos Salvos", value=stats["total_chunks"])
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="PDFs / Livros", value=stats["total_files"])
    with col_m2:
        st.metric(label="Artigos Salvos", value=stats["total_articles"])

    if stats["total_chunks"] > 0:
        if st.button("🗑️ Limpar Acervo Local", use_container_width=True):
            rag.clear_database()
            st.session_state.search_results = []
            st.warning("Acervo local limpo!")
            st.rerun()

    st.divider()
    with st.expander("🎓 Comparativo Científico para o TCC"):
        st.markdown("""
        **Bases Científicas Integradas:**
        - **PubMed Central (EUA):** Padrão mundial biomédico.
        - **SciELO Brasil:** Produção das melhores faculdades nacionais (USP, UNICAMP, UNESP, SBPqO).
        - **Europe PMC:** Acesso aberto europeu e revisões sistemáticas da Cochrane.
        - **Acervo Fechado:** Livros adotados na graduação (Malamed, Neville, Lindhe).
        """)

# CABEÇALHO PRINCIPAL
st.markdown("""
# 🦷 OdontoIA — Inteligência Artificial Multi-Bases
Consulta odontológica de alta precisão com suporte a **PubMed Central (EUA)**, **SciELO (Brasil)**, **Europe PMC** e **Livros de Referência**.
""")

# ABAS DO SISTEMA
tab_live, tab_curado, tab_coletor, tab_arquivos = st.tabs([
    "🌐 Chat 1: Busca Multi-Bases (Ao Vivo)",
    "📚 Chat 2: Meu Acervo Curado (Livros & PDFs)",
    "🔍 Coletor Científico Manual",
    "📂 Gerenciar Livros e PDFs"
])

# ==============================================================================
# ABA 1: CHAT COM BUSCA MULTI-BASES EM TEMPO REAL
# ==============================================================================
with tab_live:
    st.info("💡 **Pesquisa Ao Vivo:** Sua pergunta é pesquisada simultaneamente no **PubMed Central (EUA)**, **SciELO (Brasil)** e **Europe PMC**. A IA lê os artigos mais recentes, sintetiza a conduta clínica e transcreve os trechos exatos entre aspas com links diretos!")

    col_auto_save, _ = st.columns([2, 3])
    with col_auto_save:
        auto_save_articles = st.checkbox("📥 Salvar automaticamente os artigos encontrados no meu acervo permanente", value=False)

    # Exibição do histórico Live
    for msg in st.session_state.messages_live:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("keywords"):
                st.caption(f"🔍 Termos pesquisados nas bases: `{msg['keywords']}`")
            if msg.get("model_used"):
                st.caption(f"⚡ Modelo de IA: `{msg['model_used']}`")

            if msg.get("sources"):
                with st.expander(f"📖 Artigos Científicos Consultados ({len(msg['sources'])} trechos)"):
                    for idx, src in enumerate(msg["sources"], 1):
                        st.markdown(f"""
                        **[Artigo {idx}]** {src.get('repo_badge', '')}  
                        📄 **Título:** [{src.get('title')}]({src.get('url')})  
                        ✍️ **Autores:** {src.get('authors')} ({src.get('year')}) — *{src.get('journal')}*  
                        🔗 **DOI / Link:** [{src.get('doi') or src.get('url')}]({src.get('url')}) | **Seção:** `{src.get('page')}`  
                        > {src['text']}
                        """)

    live_query = st.chat_input("Faça sua pergunta clínica para pesquisar nas bases mundiais e nacionais...")
    if live_query:
        st.session_state.messages_live.append({"role": "user", "content": live_query})
        with st.chat_message("user"):
            st.markdown(live_query)

        with st.chat_message("assistant"):
            with st.spinner("1/3 Consultando simultaneamente PubMed, SciELO Brasil e Europe PMC..."):
                search_data = academic.live_multi_search_and_prepare_context(
                    question=live_query,
                    source_filter=selected_repo,
                    api_key=active_key,
                    max_articles=4
                )

            keywords_used = search_data.get("keywords")
            articles_found = search_data.get("articles", [])
            chunks_found = search_data.get("chunks", [])

            if not articles_found:
                answer = "⚠️ **Nenhum artigo de acesso aberto com alto nível de evidência foi localizado nas bases selecionadas para essa busca.**\n\nTente reformular com termos mais amplos ou selecione 'Todas as Bases' na barra lateral."
                st.markdown(answer)
                st.session_state.messages_live.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": [],
                    "keywords": keywords_used
                })
            else:
                if auto_save_articles:
                    for art in articles_found:
                        art_chunks = academic.fetch_article_content(art)
                        rag.add_article(art, art_chunks)

                with st.spinner(f"2/3 Lendo {len(articles_found)} artigo(s) do Brasil e do exterior e formulando conduta clínica com trechos literais..."):
                    response_data = generate_answer(
                        query=live_query,
                        context_chunks=chunks_found,
                        provider=selected_provider,
                        api_key=active_key
                    )

                st.markdown(response_data["answer"])
                if keywords_used:
                    st.caption(f"🔍 Termos pesquisados nas bases: `{keywords_used}`")
                if response_data.get("model_used"):
                    st.caption(f"⚡ Modelo de IA: `{response_data['model_used']}`")

                with st.expander(f"📖 Artigos Científicos Consultados ({len(chunks_found)} trechos)"):
                    for idx, src in enumerate(chunks_found, 1):
                        st.markdown(f"""
                        **[Artigo {idx}]** {src.get('repo_badge', '')}  
                        📄 **Título:** [{src.get('title')}]({src.get('url')})  
                        ✍️ **Autores:** {src.get('authors')} ({src.get('year')}) — *{src.get('journal')}*  
                        🔗 **DOI / Link:** [{src.get('doi') or src.get('url')}]({src.get('url')}) | **Seção:** `{src.get('page')}`  
                        > {src['text']}
                        """)

                st.session_state.messages_live.append({
                    "role": "assistant",
                    "content": response_data["answer"],
                    "sources": chunks_found,
                    "keywords": keywords_used,
                    "model_used": response_data.get("model_used")
                })

# ==============================================================================
# ABA 2: CHAT COM MEU ACERVO CURADO (LIVROS & PDFS PESSOAIS)
# ==============================================================================
with tab_curado:
    st.info("🔒 **Modo Acervo Curado (Base Fechada):** A IA consulta **apenas e exclusivamente** os livros e documentos salvos no seu acervo local (Malamed, Diretrizes do CFO, etc.). Se não constar nos seus livros, ela avisa explicitamente.")

    col1, col2, col3 = st.columns(3)
    quick_prompt_curado = None
    with col1:
        if st.button("💉 Dose Lidocaína (Malamed)", key="btn_q1", use_container_width=True):
            quick_prompt_curado = "Qual a dose máxima recomendada de lidocaína 2% com epinefrina 1:100.000 para um adulto hígido segundo a literatura de anestesiologia odontológica?"
    with col2:
        if st.button("❤️ Profilaxia Endocardite (AHA/CFO)", key="btn_q2", use_container_width=True):
            quick_prompt_curado = "Qual o protocolo atual de profilaxia antibiótica para prevenção de endocardite infecciosa em procedimentos odontológicos e quais pacientes têm indicação?"
    with col3:
        if st.button("🤰 Anestésicos em Gestantes", key="btn_q3", use_container_width=True):
            quick_prompt_curado = "Quais são as condutas e anestésicos locais de escolha para atendimento de gestantes na clínica odontológica?"

    for msg in st.session_state.messages_acervo:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("model_used"):
                st.caption(f"⚡ Modelo de IA: `{msg['model_used']}`")
            
            if msg.get("sources"):
                with st.expander(f"📖 Trechos Consultados do Seu Acervo ({len(msg['sources'])} fontes)"):
                    for idx, src in enumerate(msg["sources"], 1):
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
                            **[Fonte {idx} - Livro/Manual]** `Arquivo: {src['source']}` — **Página {src['page']}**
                            > {src['text']}
                            """)

    curado_query = st.chat_input("Consulte uma dúvida nos livros e PDFs do seu acervo...")
    if quick_prompt_curado:
        curado_query = quick_prompt_curado

    if curado_query:
        st.session_state.messages_acervo.append({"role": "user", "content": curado_query})
        with st.chat_message("user"):
            st.markdown(curado_query)

        with st.chat_message("assistant"):
            with st.spinner("Pesquisando estritamente nos PDFs e livros do seu acervo..."):
                relevant_excerpts = rag.search_relevant_excerpts(curado_query, top_k=4)

                response_data = generate_answer(
                    query=curado_query,
                    context_chunks=relevant_excerpts,
                    provider=selected_provider,
                    api_key=active_key
                )

                st.markdown(response_data["answer"])

                if response_data.get("model_used"):
                    st.caption(f"⚡ Modelo de IA: `{response_data['model_used']}`")

                if response_data.get("sources"):
                    with st.expander(f"📖 Trechos Consultados do Seu Acervo ({len(response_data['sources'])} fontes)"):
                        for idx, src in enumerate(response_data["sources"], 1):
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
                                **[Fonte {idx} - Livro/Manual]** `Arquivo: {src['source']}` — **Página {src['page']}**
                                > {src['text']}
                                """)

                st.session_state.messages_acervo.append({
                    "role": "assistant",
                    "content": response_data["answer"],
                    "sources": response_data.get("sources", []),
                    "model_used": response_data.get("model_used")
                })

# ==============================================================================
# ABA 3: COLETOR CIENTÍFICO MANUAL
# ==============================================================================
with tab_coletor:
    st.markdown("### 🔍 Coletor e Catálogo Multi-Bases (PubMed, SciELO Brasil, Europe PMC)")
    st.write("Pesquise artigos nas bases de dados abertas para selecionar e salvar permanentemente no seu acervo.")

    col_q, col_rep, col_num = st.columns([3, 2, 1])
    with col_q:
        search_query = st.text_input(
            "Pesquisar Termo Clínico:",
            placeholder="Ex: peri-implantite, clareamento sensibilidade, mepivacaina gestante"
        )
    with col_rep:
        target_repo = st.selectbox(
            "Base de Busca:",
            options=[
                ("🌐 Todas as Bases", "all"),
                ("🇧🇷 SciELO Brasil (USP, UNICAMP)", "scielo"),
                ("🇺🇸 PubMed Central (EUA)", "pubmed"),
                ("🇪🇺 Europe PMC (Europa)", "europe_pmc")
            ],
            format_func=lambda x: x[0]
        )[1]
    with col_num:
        max_articles = st.selectbox("Quantidade por Base:", options=[1, 2, 3], index=1)

    if st.button("🔍 Buscar nas Bases Científicas", type="primary"):
        if not search_query.strip():
            st.warning("Por favor, digite um tema para pesquisar.")
        else:
            with st.spinner("Pesquisando nas bases selecionadas..."):
                results = academic.search_all_sources(
                    query=search_query,
                    source_filter=target_repo,
                    max_per_source=max_articles,
                    study_type="all_evidence",
                    api_key=active_key
                )
                st.session_state.search_results = results
                if not results:
                    st.warning("Nenhum artigo encontrado. Tente termos sinônimos ou selecione 'Todas as Bases'.")

    if st.session_state.search_results:
        st.write(f"### 📄 Artigos Encontrados ({len(st.session_state.search_results)})")
        
        if st.button("📥 Salvar TODOS os Artigos Encontrados no Acervo Permanente", use_container_width=True):
            pbar = st.progress(0)
            status_box = st.empty()
            total_indexed = 0
            for i, art in enumerate(st.session_state.search_results):
                status_box.text(f"Indexando: {art['title'][:60]}...")
                chunks = academic.fetch_article_content(art)
                count = rag.add_article(art, chunks)
                total_indexed += count
                pbar.progress((i + 1) / len(st.session_state.search_results))
            status_box.success(f"Concluído! {total_indexed} trechos científicos salvos no acervo permanente.")
            st.rerun()

        st.divider()

        for i, art in enumerate(st.session_state.search_results):
            with st.container():
                st.markdown(f"#### {i+1}. {art.get('repo_badge', '')} [{art['title']}]({art['url']})")
                st.markdown(f"**Autores:** {art['authors']} | **Revista:** *{art['journal']}* ({art['year']})")
                badge_doi = f"**DOI:** [{art['doi']}](https://doi.org/{art['doi']})" if art.get("doi") else ""
                st.markdown(f"**Origem:** `{art['source_repo']}` | {badge_doi}")

                if st.button(f"📥 Salvar este Artigo no Acervo", key=f"btn_art_multi_{art['id']}"):
                    with st.spinner("Indexando..."):
                        chunks = academic.fetch_article_content(art)
                        added_count = rag.add_article(art, chunks)
                        st.success(f"Salvo com sucesso! ({added_count} trechos mapeados no acervo permanente).")
                        st.rerun()
                st.divider()

# ==============================================================================
# ABA 4: GERENCIAR LIVROS E PDFS
# ==============================================================================
with tab_arquivos:
    st.markdown("### 📂 Gerenciamento de Documentos e PDFs Locais")
    
    st.subheader("Subir Livros e Manuais em PDF")
    uploaded_files = st.file_uploader(
        "Selecione arquivos PDF de livros (ex: Malamed, Lindhe, Neville, Cohen):",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("📥 Processar e Indexar PDFs Selecionados", type="primary"):
            pbar = st.progress(0)
            status_box = st.empty()
            total_added = 0
            for idx, uploaded_file in enumerate(uploaded_files):
                status_box.text(f"Processando: {uploaded_file.name}...")
                save_path = os.path.join(DOCUMENTS_PATH, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                chunks_count = rag.add_pdf(save_path)
                total_added += chunks_count
                pbar.progress((idx + 1) / len(uploaded_files))

            status_box.success(f"Sucesso! {len(uploaded_files)} PDF(s) indexado(s) com {total_added} trechos mapeados.")
            st.rerun()

    st.divider()

    articles = rag.get_indexed_articles()
    st.subheader(f"📄 Artigos Salvos no Acervo Permanente ({len(articles)})")
    if not articles:
        st.info("Nenhum artigo salvo manualmente ainda.")
    else:
        for art in articles:
            with st.expander(f"🔬 {art.get('repo_badge', '')} {art.get('title')} ({art.get('year')})"):
                st.markdown(f"**Autores:** {art.get('authors')}")
                st.markdown(f"**Revista:** *{art.get('journal')}* | **Trechos:** `{art.get('chunks_count', '?')}`")
                st.markdown(f"🔗 [Acessar Artigo]({art.get('url')})")

    st.divider()
    st.subheader(f"📘 Arquivos de Livros e Manuais no Disco ({len(stats['files'])})")
    for f in stats["files"]:
        st.write(f"- 📕 **{f}**")
