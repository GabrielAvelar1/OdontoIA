# ✨ OdontoMind — Agente Híbrido de Inteligência Artificial para Odontologia Baseada em Evidências

> **Projeto de Pesquisa & Trabalho de Conclusão de Curso (TCC)**  
> Sistema de Suporte à Decisão Clínica (*Hybrid Agentic RAG — Metodologia ECC*) com busca automatizada em tempo real no **PubMed Central (EUA)**, **SciELO Brasil (OpenAlex)** e **Europe PMC**, combinada a um **Compêndio Clínico Padrão-Ouro** de livros-texto clássicos da Odontologia.

---

## 🎯 Por que este projeto é relevante para o TCC?

Um dos maiores desafios no uso de inteligências artificiais na área da saúde é a ocorrência de **alucinações clínicas** ou falhas de recuperação quando o estudante faz perguntas práticas de clínica/cirurgia (ex: *"Qual o passo a passo de uma extração de dentes posteriores?"*) e as bases retornam apenas artigos em inglês técnico sem traduzir ou sintetizar o protocolo.

O **OdontoMind** resolve isso por meio da arquitetura **ECC Hybrid Agentic RAG**:
1. **Planejador Bilíngue de Consultas (MeSH & DeCS):** Converte perguntas naturais em português para descritores clínicos estruturados em inglês (PubMed/Europe PMC) e português limpo sem *stopwords* (SciELO Brasil), identificando automaticamente se a intenção é um **Protocolo Clínico / Passo a Passo** ou uma **Síntese de Evidências / Comparação**.
2. **Reranking Seccional e Semântico de Artigo Completo:** Em vez de ler apenas a introdução dos artigos, o motor avalia todas as seções do XML/texto completo e prioriza **Métodos, Técnica Cirúrgica, Resultados, Discussão e Conclusões**.
3. **Fusão Híbrida (Multi-Bases Ao Vivo + Compêndio Clínico Padrão-Ouro):** Combina em tempo real os artigos científicos mundiais com o **Compêndio Clínico Padrão-Ouro** integrado ao sistema:
   - **Cirurgia Bucomaxilofacial (Hupp, Ellis & Tucker — Peterson):** Passo a passo da exodontia de posteriores e anteriores, sindesmotomia, alavancas, numeração de fórceps (150, 151, 17, 18R, 18L, 23, 65, 69), odontosecção, osteotomia, alveolite e comunicação bucossinusal.
   - **Anestesiologia Local (Stanley F. Malamed):** Cálculo de doses máximas por peso e teto absoluto, limites em cardiopatas e passo a passo dos bloqueios regionais maxilares e mandibulares.
   - **Farmacologia e Profilaxia (Eduardo Dias de Andrade & AHA/CFO):** Profilaxia da endocardite infecciosa, protocolos analgésicos, anti-inflamatórios e antibióticos, além de atendimento a gestantes.
   - **Endodontia (Cohen & Lopes e Siqueira):** Diagnóstico pulpar/periapical e passo a passo do tratamento endodôntico (acesso, odontometria, PQM, NaOCl, EDTA/PUI e obturação).
   - **Periodontia e Implantodontia (Jan Lindhe & AAP/EFP):** Classificação em Estágios e Graus, terapia periodontal e numeração específica das curetas de Gracey (1-2 a 13-14).
   - **Dentística Restauradora (Baratieri & Anusavice):** Condicionamento ácido seletivo, sistemas adesivos, inserção incremental (Fator-C) e proteção do complexo dentino-pulpar.
   - **Estomatologia e Patologia Oral (Neville):** Passo a passo da biópsia incisional vs excisional e diagnóstico diferencial de cistos e tumores odontogênicos.
4. **Tradução Clínica Ativa e Comprovação Textual Bilíngue:**
   - **Trechos Literais Entre Aspas (`"..."`):** Toda resposta transcreve os fragmentos originais exatos utilizados e sua localização (Livro/Página ou Autores/Ano/Revista/Seção/DOI).
   - **Tradução Técnica Imediata:** Quando o trecho citado vem de um artigo em inglês do PubMed ou Europe PMC, o sistema apresenta o trecho original entre aspas seguido de sua tradução técnica em português.

---

## 🚀 Como Iniciar a Aplicação

### Modo Rápido (1 Clique no Windows):
Dê dois cliques no arquivo **`run.bat`** na pasta do projeto.

### Modo Linha de Comando:
```powershell
.venv\Scripts\streamlit.exe run app.py
```
