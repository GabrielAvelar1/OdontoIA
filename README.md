# 🦷 OdontoIA — Inteligência Artificial Baseada em Evidências para Odontologia

> **Projeto de Pesquisa & Trabalho de Conclusão de Curso (TCC)**  
> Sistema RAG (*Retrieval-Augmented Generation*) para suporte à decisão clínica e consulta bibliográfica estritamente fundamentada em livros e artigos científicos de Odontologia, integrado com a API oficial do **PubMed Central (NCBI)**.

---

## 🎯 Por que este projeto é relevante para o TCC?

Um dos maiores problemas no uso de inteligências artificiais na saúde (como ChatGPT ou buscas no Google) é a ocorrência de **alucinações clínicas**: condutas terapêuticas desatualizadas, dosagens incorretas ou invenção de diretrizes inexistentes.

A **OdontoIA** resolve isso por meio de **Odontologia Baseada em Evidências (OBE)**:
1. **Sem alucinações:** A IA só responde utilizando trechos literais dos livros e artigos catalogados no acervo.
2. **Coletor Automatizado Multi-Bases (Open Access):**
   - 🇺🇸 **PubMed Central (EUA / NLM):** Padrão mundial biomédico.
   - 🇧🇷 **SciELO Brasil (USP, UNICAMP, UNESP, SBPqO):** Estudos nacionais e epidemiologia brasileira.
   - 🇪🇺 **Europe PMC (Europa):** Acesso aberto europeu e revisões sistemáticas da Cochrane.
3. **Citação, Rastreabilidade e Comprovação Textual:**
   - **Trechos Literais Entre Aspas ("..."):** Toda resposta traz uma seção dedicada transcrevendo os fragmentos exatos utilizados do texto original.
   - **Localização Rígida:** Para livros, aponta arquivo e página exata; para artigos, aponta autores, ano, revista, base de dados (PubMed/SciELO/Europe PMC), seção clínica, DOI e link direto.
4. **Curadoria do Aluno/Pesquisador:** Você escolhe o acervo padrão-ouro (Malamed, Lindhe, Neville, Cohen, Diretrizes CFO/ABO/AHA e revisões da Cochrane).

---

## 🚀 Como Iniciar a Aplicação

### Modo Rápido (1 Clique):
Basta dar dois cliques no arquivo **`run.bat`** na pasta do projeto. O navegador abrirá automaticamente com a interface.

### Modo Linha de Comando:
```powershell
.venv\Scripts\streamlit.exe run app.py
```

---

## 💡 Como Usar a Interface

1. **Obter chave de IA gratuita:**
   - Na barra lateral, selecione **Gemini (Recomendado)**.
   - Crie uma chave gratuita em segundos no [Google AI Studio](https://aistudio.google.com/app/apikey) e cole no campo.
2. **Buscar Artigos Científicos no PubMed:**
   - Acesse a aba **"🌐 Coletor PubMed (Open Access)"**.
   - Digite o tema (ex: *peri-implantite*, *clareamento sensibilidade*, *profilaxia endocardite*).
   - Escolha o nível de evidência (Revisões Sistemáticas / Ensaios Clínicos).
   - Clique em **"Indexar este Artigo"** ou **"Indexar TODOS"**. O sistema baixa o texto completo e fatiará em trechos com DOI e links.
3. **Adicionar seus próprios livros:**
   - Na aba **"📚 Gerenciar Acervo & PDFs"**, envie PDFs de capítulos dos seus livros e clique em processar.
4. **Fazer Perguntas Clínicas:**
   - Na aba **"💬 Chat Clínico"**, faça perguntas ou use as perguntas rápidas e veja a IA responder citando as fontes exatas!

---

## 🔬 Estrutura Científica e Metodológica para o seu TCC

* **Título Sugerido:**  
  *Desenvolvimento e Validação de um Sistema de Recuperação Aumentada por Geração (RAG) Integrado à API do PubMed para Tomada de Decisão Clínica Baseada em Evidências na Odontologia.*
* **Objetivo Geral:**  
  Desenvolver um protótipo de IA especialista alimentado exclusivamente por literatura odontológica validada (Open Access PubMed + Manuais Clínicos) e mensurar sua acurácia clínica contra modelos genéricos.
* **Metodologia de Validação (Avaliação por Painel):**  
  1. Elaborar um banco com 30 a 50 questões clínicas desafiadoras (ex: Anestesiologia em cardiopatas, farmacologia em gestantes, conduta em peri-implantite, profilaxia antibiótica).
  2. Submeter as perguntas à OdontoIA e a uma IA genérica comercial (ex: ChatGPT padrão).
  3. Painel avaliador cego com 2 professores/especialistas avaliando:
     - **Precisão da conduta** (Correta / Incorreta / Parcial).
     - **Rastreabilidade bibliográfica** (Presença de autor, ano, DOI/página).
     - **Taxa de alucinação** (Frequência de erros factuais ou condutas inventadas).
