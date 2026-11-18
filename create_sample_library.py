import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

PDF_FILENAME = "Compendio_Clinico_Odontologia_Padrao_Ouro.pdf"

def generate_sample_pdf(target_dir: str = None) -> str:
    if target_dir is None:
        target_dir = os.path.join(os.path.dirname(__file__), "documents")
    os.makedirs(target_dir, exist_ok=True)
    pdf_path = os.path.join(target_dir, PDF_FILENAME)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    normal_style.fontSize = 9.5
    normal_style.leading = 13.5

    story = []

    # PÁGINA 1: CAPA E SUMÁRIO
    story.append(Paragraph("Compêndio Clínico de Odontologia Baseada em Evidências — Padrão-Ouro", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Referências Bibliográficas Consagradas integradas neste Compêndio:</b>", normal_style))
    story.append(Paragraph(
        "1. <b>Anestesiologia:</b> MALAMED, S. F. Manual de Anestesia Local. 7ª ed. Elsevier.<br/>"
        "2. <b>Cirurgia Bucomaxilofacial:</b> HUPP, J. R.; ELLIS, E.; TUCKER, M. R. Cirurgia Oral e Maxilofacial Contemporânea (Peterson). 7ª ed.<br/>"
        "3. <b>Terapêutica e Farmacologia:</b> ANDRADE, E. D. Terapêutica Medicamentosa em Odontologia. 3ª ed. Artes Médicas; Diretrizes AHA/CFO.<br/>"
        "4. <b>Endodontia:</b> HARGREAVES, K. M.; BERMAN, L. H. Caminhos da Polpa (Cohen). 12ª ed.; LOPES, H. P.; SIQUEIRA JR, J. F. Endodontia: Biologia e Técnica.<br/>"
        "5. <b>Periodontia e Implantodontia:</b> LINDHE, J.; LANG, N. P. Tratado de Periodontia Clínica e Implantologia Oral. 6ª ed.; Classificação AAP/EFP 2018.<br/>"
        "6. <b>Dentística e Materiais Dentários:</b> BARATIERI, L. N. Odontologia Restauradora: Fundamentos e Técnicas; ANUSAVICE, K. J. Materiais Dentários de Phillips.<br/>"
        "7. <b>Patologia Oral e Estomatologia:</b> NEVILLE, B. W. et al. Patologia Oral e Maxilofacial. 4ª ed.",
        normal_style
    ))
    story.append(PageBreak())

    # PÁGINA 2: CAPÍTULO 1 - ANESTESIOLOGIA E DOSES MÁXIMAS (MALAMED)
    story.append(Paragraph("Capítulo 1: Anestésicos Locais em Odontologia — Doses Máximas e Cálculos (Malamed)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    Segundo Stanley F. Malamed (Manual de Anestesia Local, 7ª ed.):<br/><br/>
    <b>1. Cloridrato de Lidocaína 2% com Epinefrina 1:100.000 ou 1:200.000:</b><br/>
    - É o anestésico local padrão-ouro em odontologia mundial.<br/>
    - Dose máxima recomendada por peso corpóreo: <b>4,4 mg/kg</b>, não devendo ultrapassar o teto máximo absoluto de <b>300 mg</b> por sessão clínica em pacientes adultos hígidos (ASA I).<br/>
    - Cada tubete odontológico de 1,8 mL de solução a 2% contém exatamente <b>36 mg</b> de cloridrato de lidocaína e 0,018 mg de epinefrina (na concentração 1:100.000) ou 0,009 mg (na concentração 1:200.000).<br/>
    - Portanto, o número máximo de tubetes de lidocaína 2% com epinefrina 1:100.000 para um adulto hígido de 70 kg é de aproximadamente <b>8 tubetes</b> (300 mg / 36 mg = 8,33 tubetes).<br/><br/>
    <b>2. Cloridrato de Articaína 4% com Epinefrina 1:100.000 ou 1:200.000:</b><br/>
    - Dose máxima recomendada: <b>7,0 mg/kg</b> (teto absoluto de <b>500 mg</b>). Cada tubete de 1,8 mL a 4% contém <b>72 mg</b> de articaína (máximo de ~7 tubetes para adulto de 70 kg).<br/>
    - Possui anel tiofeno e biotransformação mista (plasma por colinesterases + fígado), meia-vida plasmática curta (~27 min) e alta difusibilidade óssea, permitindo anestesia infiltrativa vestibular eficaz inclusive em região de pré-molares e molares inferiores como complemento. Evitar no bloqueio regional do nervo alveolar inferior devido ao risco aumentado de parestesia.<br/><br/>
    <b>3. Cloridrato de Mepivacaína 2% com Epinefrina 1:100.000 ou Mepivacaína 3% sem vasoconstritor:</b><br/>
    - Dose máxima recomendada: <b>4,4 mg/kg</b> (teto absoluto de <b>300 mg</b>).<br/>
    - Na apresentação 2% com vasoconstritor, cada tubete tem 36 mg (máx. 8 tubetes). Na apresentação 3% sem vasoconstritor, cada tubete tem <b>54 mg</b> (máx. 5,5 tubetes para adulto de 70 kg). É o sal com menor efeito vasodilatador intrínseco, sendo a primeira escolha quando há contraindicação absoluta a vasoconstritores adrenérgicos.<br/><br/>
    <b>4. Cloridrato de Prilocaína 3% com Felipressina 0,03 UI/mL:</b><br/>
    - Dose máxima recomendada: <b>6,0 mg/kg</b> (teto máximo absoluto de <b>400 mg</b>). Cada tubete de 1,8 mL contém 54 mg de prilocaína (máx. ~7 tubetes). Contraindicada em gestantes, anêmicos e portadores de meta-hemoglobinemia.<br/><br/>
    <b>5. Cloridrato de Bupivacaína 0,5% com Epinefrina 1:200.000:</b><br/>
    - Dose máxima recomendada: <b>1,3 mg/kg</b> (teto absoluto de <b>90 mg</b>). Cada tubete de 1,8 mL contém 9 mg (máx. 10 tubetes). Indicada para procedimentos cirúrgicos longos e controle de dor pós-operatória (duração pulpar de 90-180 min e tecidos moles de 4 a 9 horas).<br/><br/>
    <b>6. Limite de Vasoconstritor (Epinefrina) em Cardiopatas (ASA III):</b><br/>
    - Adultos saudáveis (ASA I): dose máxima de epinefrina é <b>0,2 mg</b> por sessão (~11 tubetes de 1:100.000).<br/>
    - Pacientes cardiopatas compensados (ASA III): dose máxima de epinefrina é <b>0,04 mg</b> por sessão, o que equivale a no máximo <b>2 tubetes de epinefrina 1:100.000</b> ou <b>4 tubetes de epinefrina 1:200.000</b>.
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 3: CAPÍTULO 2 - TÉCNICAS ANESTÉSICAS MAXILARES E MANDIBULARES (MALAMED)
    story.append(Paragraph("Capítulo 2: Passo a Passo das Técnicas Anestésicas Maxilares e Mandibulares (Malamed)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    Segundo Stanley F. Malamed (Manual de Anestesia Local):<br/><br/>
    <b>1. Técnicas para Extração e Procedimentos em Dentes Posteriores da Mandíbula (Tríade Mandibular):</b><br/>
    Para exodontia de molares e pré-molares inferiores, devido à espessura da cortical óssea mandibular, realiza-se o bloqueio regional:<br/>
    - <b>Bloqueio do Nervo Alveolar Inferior (BNAI):</b> Agulha longa (25G ou 27G). Pontos de reparo: incisura coronóide (depressão máxima na borda anterior do ramo da mandíbula), rafe pterigomandibular e plano oclusal dos molares inferiores. Posiciona-se o corpo da seringa sobre os pré-molares do lado oposto (contralateral), introduz-se a agulha 6 a 10 mm acima do plano oclusal dos molares inferiores até tocar suavemente o osso da face medial do ramo (profundidade média de <b>20 a 25 mm</b>, cerca de 2/3 a 3/4 da agulha longa). Recua-se 1 mm, realiza-se aspiração prévia em dois planos e deposita-se 1,5 mL lentamente (mínimo 60 segundos).<br/>
    - <b>Bloqueio do Nervo Lingual:</b> Realizado no mesmo trajeto do BNAI, recuando a agulha até metade da profundidade (~10-15 mm) ou depositando 0,3 mL durante a retirada.<br/>
    - <b>Bloqueio do Nervo Bucal (Longo Bucal):</b> Essencial para exodontia de molares inferiores (anestesia o mucoperiósteo e gengiva vestibular dos molares inferiores). Ponto de punção: mucosa distal e vestibular ao último molar inferior, com bisel voltado para o osso, profundidade de 2 a 4 mm, depositando 0,3 mL.<br/><br/>
    <b>2. Técnicas para Extração e Procedimentos em Dentes Posteriores da Maxila:</b><br/>
    - <b>Bloqueio do Nervo Alveolar Superior Posterior (ASP):</b> Anestesia 3º, 2º e 1º molares superiores (exceto a raiz mesiovestibular do 1º molar superior em 28% dos pacientes). Agulha curta (27G), inserida na altura da prega mucovestibular acima do 2º molar superior, com angulação de <b>45 graus</b> para cima, para dentro e para trás, profundidade de 16 mm, aspiração prévia obrigatória (risco de hematoma no plexo venoso pterigóideo) e depósito de 0,9 a 1,8 mL.<br/>
    - <b>Bloqueio do Nervo Alveolar Superior Médio (ASM) ou Supraperiosteal:</b> Acima do 2º pré-molar superior para anestesiar 1º e 2º pré-molares e a raiz mesiovestibular do 1º molar superior.<br/>
    - <b>Bloqueio do Nervo Palatino Maior:</b> Obrigatório para exodontia de dentes posteriores superiores (anestesia o mucoperiósteo palatino do 3º molar até o 1º pré-molar). Ponto de punção: tecido mole levemente anterior ao forame palatino maior (localizado na junção entre o processo alveolar maxilar e o osso palatino, medial ao 2º ou 3º molar superior, a ~1 cm da margem gengival palatina), depositando 0,45 a 0,6 mL sob pressão controlada.
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 4: CAPÍTULO 3 - PASSO A PASSO DA EXODONTIA DE DENTES POSTERIORES E ANTERIORES (HUPP / PETERSON)
    story.append(Paragraph("Capítulo 3: Passo a Passo da Extração Dentária (Exodontia de Posteriores e Anteriores) — Hupp / Peterson", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    Segundo Hupp, Ellis & Tucker (Cirurgia Oral e Maxilofacial Contemporânea - Peterson, 7ª ed.):<br/><br/>
    <b>PASSO A PASSO COMPLETO DA EXTRAÇÃO DE DENTES POSTERIORES (TEMPOS OPERATÓRIOS DA EXODONTIA):</b><br/><br/>
    <b>Passo 1 — Avaliação Radiográfica, Antissepsia, Anestesia e Posicionamento:</b><br/>
    - Avaliar na radiografia periapical/panorâmica a configuração radicular (divergência, dilaceração, hipercementose) e relação com estruturas nobres (seio maxilar nos posteriores superiores e canal mandibular/forame mentual nos posteriores inferiores).<br/>
    - Antissepsia intraoral com digluconato de clorexidina 0,12% (bochecho por 1 minuto) e extraoral com clorexidina 2%.<br/>
    - Anestesia local adequada: para posteriores superiores (ASP + ASM/supraperiosteal + Palatino Maior); para posteriores inferiores (BNAI + Lingual + Bucal).<br/>
    - Posicionamento da cadeira: Para exodontia em <b>maxila</b>, o plano oclusal maxilar deve ficar a 60° com o solo e a boca do paciente na altura dos ombros/cotovelos do cirurgião. Para exodontia em <b>mandíbula</b>, o paciente fica mais sentado, com o plano oclusal mandibular paralelo ao solo quando a boca está aberta.<br/><br/>
    <b>Passo 2 — Sindesmotomia (Descolamento Gengival / Diérese):</b><br/>
    - Utiliza-se o <b>descolador de Molt nº 9</b> ou <b>sindesmótomo</b> para descolar a papila interdental e as fibras do ligamento gengivodental (inserção conjuntiva) em toda a circunferência cervical do dente (vestibular, lingual/palatina, mesial e distal) até a crista óssea alveolar.<br/>
    - <i>Objetivo clínico:</i> Confirmar a eficácia da anestesia e permitir que as pontas ativas do fórceps e as alavancas sejam posicionadas o mais apicalmente possível sob a gengiva, evitando laceração gengival.<br/><br/>
    <b>Passo 3 — Luxação Inicial com Alavancas (Extratores):</b><br/>
    - Utiliza-se uma <b>alavanca reta</b> (ex: alavanca apical reta nº 301 ou Seldin reta) inserida perpendicularmente ao longo eixo do dente no espaço interproximal mesial/vestibular, apoiada <b>exclusivamente na crista óssea alveolar interdental</b> (nunca usar o dente vizinho saudável como fulcro/apoio para não luxá-lo!).<br/>
    - Aplicam-se movimentos de cunha e de roda-e-eixo (pequenas rotações controladas) para expandir o alvéolo ósseo e iniciar a ruptura das fibras do ligamento periodontal. A mão oposta do cirurgião (mão não dominante) deve obrigatoriamente estabilizar as tábuas ósseas vestibular e lingual/palatina ("pinça digital") e sustentar a mandíbula para proteger a ATM.<br/><br/>
    <b>Passo 4 — Adaptação e Apreensão com o Fórceps Cirúrgico Específico para Dentes Posteriores:</b><br/>
    - As pontas ativas (mordentes) do fórceps devem ser adaptadas abaixo do tecido gengival descolado, abraçando a superfície radicular (colo anatômico) paralelas ao longo eixo do dente. Adapta-se primeiro a ponta lingual/palatina e em seguida a vestibular.<br/>
    - <b>Escolha do Fórceps para Dentes Posteriores:</b><br/>
      * <b>Pré-molares Superiores:</b> Fórceps <b>nº 150</b> (universal superior).<br/>
      * <b>Molares Superiores (Direito e Esquerdo):</b> Fórceps <b>nº 18R</b> (lado direito) e <b>nº 18L</b> (lado esquerdo). A ponta ativa com esporão/garra encaixa-se na furca vestibular (entre as raízes mesiovestibular e distovestibular) e a ponta ativa lisa e côncava adapta-se na raiz palatina.<br/>
      * <b>Pré-molares Inferiores:</b> Fórceps <b>nº 151</b> (universal inferior).<br/>
      * <b>Molares Inferiores (ambos os lados):</b> Fórceps <b>nº 17</b> (possui garras pontiagudas em ambas as pontas ativas para encaixar nas bifurcações vestibular e lingual) ou Fórceps <b>nº 23 / nº 16 ("Chifre de Vaca")</b>, cujas pontas cônicas curvas penetram na furca entre as raízes mesial e distal, promovendo luxação e elevação vertical.<br/>
      * <b>Raízes residuais posteriores superiores:</b> Fórceps <b>nº 65</b> (baioneta) ou <b>nº 69</b>.<br/><br/>
    <b>Passo 5 — Luxação Propriamente Dita e Avulsão (Movimentos do Fórceps em Posteriores):</b><br/>
    - <b>1º Movimento (Pressão Apical):</b> Empurrar firme o fórceps em direção ao fundo do alvéolo para deslocar o centro de rotação apicalmente (reduzindo o risco de fratura radicular) e expandir a crista óssea.<br/>
    - <b>2º Movimento (Expansão Vestibulolingual / Vestibulopalatina):</b> Aplicação de força lenta, contínua e crescente alternando para vestibular e para lingual/palatino. Na maxila posterior, a cortical vestibular é mais delgada que a palatina, predominando a expansão vestibular (com cautela no 1º molar superior devido ao pilar zigomaticoalveolar). Na mandíbula posterior, nos 2º e 3º molares a cortical lingual é mais fina que a vestibular (reforçada pela linha oblíqua externa), devendo-se equilibrar o movimento vestibulolingual. <i>Atenção: Movimentos de rotação são contraindicados em molares e no 1º pré-molar superior birradicular!</i><br/>
    - <b>3º Movimento (Tração / Avulsão):</b> Após a expansão cortical e ruptura do ligamento periodontal, retira-se o dente com força suave de tração geralmente no sentido vestibulo-oclusal.<br/><br/>
    <b>Passo 6 — Exodontia a Retalho (Técnica Aberta / Terceiro Tempo — Quando Indispensável):</b><br/>
    - Se houver resistência excessiva, coroa destruída, hipercementose ou raízes divergentes em posteriores: realizar incisão com lâmina nº 15 (retalho em envelope ou triangular), descolamento mucoperiosteal com Molt nº 9, <b>osteotomia vestibular</b> e <b>odontosecção</b> (separação das raízes dos molares na furca com broca Zekrya ou 702 em alta rotação sob irrigação abundante com soro fisiológico 0,9% estéril), removendo cada raiz individualmente com alavancas (Seldin 1L/1R, Apexo 302/303 ou Potts).<br/><br/>
    <b>Passo 7 — Toalete do Alvéolo, Manobra de Chompret, Hemostasia e Sutura (Síntese):</b><br/>
    - Inspecionar o dente extraído para confirmar integridade dos ápices radiculares.<br/>
    - Curetagem do fundo do alvéolo com <b>cureta de Lucas nº 85/86</b> apenas se houver lesão periapical (granuloma/cisto) ou fragmentos ósseos/cálculo. Limar espículas ósseas com lima para osso ou pinça goiva.<br/>
    - Irrigação abundante do alvéolo com soro fisiológico estéril 0,9%.<br/>
    - <b>Manobra de Chompret:</b> Compressão bidigital das corticais vestibular e lingual/palatina para reposicionar as tábuas ósseas expandidas.<br/>
    - <b>Sutura:</b> Com porta-agulha Mayo-Hegar, pinça dente de rato/Adson e fio de Nylon 4-0 ou Seda 3-0/4-0 (ponto simples, em "X" ou em "8" sobre o alvéolo para estabilizar o coágulo e aproximar as papilas), seguida de compressão local com gaze estéril umedecida por 20 a 30 minutos.
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 5: CAPÍTULO 4 - COMPLICAÇÕES CIRÚRGICAS E ATENDIMENTO A GESTANTES (HUPP / MALAMED)
    story.append(Paragraph("Capítulo 4: Complicações Pós-Exodontia e Atendimento a Pacientes Gestantes (Hupp & Malamed)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    <b>1. Diagnóstico e Conduta na Alveolite (Osteíte Alveolar Pós-Exodontia — Hupp):</b><br/>
    - Ocorre tipicamente entre o <b>3º e o 5º dia pós-operatório</b> após perda ou lise prematura do coágulo sanguíneo.<br/>
    - Quadro clínico: dor severa, pulsátil e irradiada para ouvido/têmpora, alvéolo vazio com osso exposto, odor fétido (halitose) e ausência de sinais sistêmicos de infecção.<br/>
    - <b>Conduta clínica passo a passo:</b> 1. Anestesia local (preferencialmente bloqueio regional sem vasoconstritor ou distante para não isquemiar ainda mais o alvéolo); 2. Irrigação abundante e suave com soro fisiológico 0,9% morno ou clorexidina 0,12% para remover detritos alimentares; 3. <b>NÃO realizar curetagem agressiva</b> das paredes ósseas do alvéolo seco (a raspagem do osso necrótico expõe mais osso viável e piora a dor); 4. Aplicação opcional de curativo sedativo intra-alveolar (ex: pasta à base de eugenol/Alveolex trocada a cada 48h) e prescrição de analgésicos potentes (Dipirona 1g de 6/6h).<br/><br/>
    <b>2. Comunicação Bucossinusal (CBS) em Exodontia de Posteriores Superiores:</b><br/>
    - Diagnóstico: inspeção cuidadosa e Manobra de Valsalva suave (observar borbulhamento pelo alvéolo; evitar assoprar com força excessiva para não romper membrana sinusal íntegra).<br/>
    - Conduta imediata: comunicações pequenas (≤ 2 mm) fecham espontaneamente com manutenção do coágulo, sutura oclusiva em "8" e cuidados sinusais (não assoar o nariz, espirrar de boca aberta, evitar canudos por 14 dias). Comunicações médias (2 a 6 mm): esponja hemostática de colágeno/gelatina (Hemospon) + sutura oclusiva + Amoxicilina 500mg 8/8h por 7 dias + descongestionante nasal. Comunicações grandes (> 6 mm): fechamento primário imediato com retalho vestibular deslizante de avanço (incisões relaxantes no periósteo).<br/><br/>
    <b>3. Protocolo Odontológico para Atendimento de Gestantes (Malamed & Andrade):</b><br/>
    - <b>Período mais seguro:</b> O <b>segundo trimestre gestacional (da 14ª à 27ª semana)</b> é o período eletivo ideal. Urgências odontológicas (pulpites, abscessos, traumatismos) devem ser atendidas em qualquer trimestre.<br/>
    - <b>Anestésico de escolha:</b> <b>Lidocaína 2% com epinefrina 1:100.000 ou 1:200.000</b> (Categoria B da FDA), limite prudente de 2 tubetes por sessão com aspiração negativa e injeção lenta.<br/>
    - <b>Contraindicações:</b> Prilocaína com felipressina (risco de meta-hemoglobinemia fetal e efeito ocitócico teórico da felipressina), Articaína e Bupivacaína (Categoria C).<br/>
    - <b>Fármacos seguros na gestante:</b> Analgésico de escolha é o <b>Paracetamol (500 a 750 mg de 6/6h)</b>. Antibióticos seguros: <b>Penicilinas (Amoxicilina 500 mg 8/8h) e Cefalosporinas (Categoria B)</b>; em alérgicas, Azitromicina ou Clindamicina. <b>Contraindicados:</b> AINEs (especialmente no 3º trimestre pelo risco de fechamento precoce do ducto arterioso fetal) e Tetraciclinas.<br/>
    - <b>Posição na cadeira:</b> No 3º trimestre, posicionar em decúbito lateral esquerdo (inclinação de 15° com almofada sob o quadril direito) para evitar a Síndrome da Hipotensão Supina por compressão da veia cava inferior.
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 6: CAPÍTULO 5 - PROFILAXIA DE ENDOCARDITE E FARMACOLOGIA CLÍNICA (AHA / CFO / ANDRADE)
    story.append(Paragraph("Capítulo 5: Profilaxia Antibiótica da Endocardite e Terapêutica Medicamentosa (AHA / CFO / Andrade)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    De acordo com as diretrizes atualizadas da American Heart Association (AHA 2021), Sociedade Brasileira de Cardiologia (SBC), Conselho Federal de Odontologia (CFO) e Eduardo Dias de Andrade:<br/><br/>
    <b>1. Pacientes de Alto Risco com Indicação Formal de Profilaxia para Endocardite Infecciosa:</b><br/>
    - Portadores de prótese valvar cardíaca mecânica ou biológica (incluindo TAVI e homoenxertos).<br/>
    - Pacientes com episódio prévio documentado de endocardite infecciosa.<br/>
    - Cardiopatias congênitas cianóticas não corrigidas (incluindo shunts e condutos paliativos), cardiopatias congênitas corrigidas com material protético nos primeiros 6 meses pós-operatórios, ou com defeito residual adjacente ao material protético.<br/>
    - Receptores de transplante cardíaco que desenvolveram valvopatia cardíaca.<br/>
    <i>Nota: Prolapso de valva mitral, febre reumática sem lesão valvar protética, marca-passo e stents coronarianos NÃO possuem indicação de profilaxia antibiótica para procedimentos dentários.</i><br/><br/>
    <b>2. Procedimentos Odontológicos que Exigem Profilaxia:</b><br/>
    - Todos os procedimentos que envolvam manipulação de tecido gengival, região periapical do dente ou perfuração da mucosa oral (exodontias, raspagem periodontal, cirurgia periapical, instalação de implantes, biópsias, colocação de bandas ortodônticas subgengivais).<br/><br/>
    <b>3. Esquema Posológico da Profilaxia (Dose Única 30 a 60 minutos antes do procedimento):</b><br/>
    - <b>Adultos (Via Oral — Padrão):</b> <b>Amoxicilina 2 g</b> VO em dose única.<br/>
    - <b>Crianças (Via Oral — Padrão):</b> <b>Amoxicilina 50 mg/kg</b> VO em dose única (máximo 2 g).<br/>
    - <b>Alérgicos a Penicilinas (Via Oral — Adultos):</b> <b>Azitromicina 500 mg</b> VO, <b>Claritromicina 500 mg</b> VO, <b>Doxiciclina 100 mg</b> VO, ou <b>Cefalexina 2 g</b> VO (somente se não houver histórico de anafilaxia, angioedema ou urticária imediata à penicilina).<br/>
    - <b>Alérgicos a Penicilinas (Via Oral — Crianças):</b> Azitromicina ou Claritromicina <b>15 mg/kg</b> VO.<br/>
    - <i>Alerta Clínico AHA 2021:</i> A <b>Clindamicina NÃO é mais recomendada</b> na profilaxia da endocardite infecciosa devido ao alto índice de reações adversas graves e colite pseudomembranosa por <i>Clostridioides difficile</i>.<br/><br/>
    <b>4. Protocolos de Prescrição Pós-Operatória em Cirurgia Odontológica (Andrade):</b><br/>
    - <b>Analgesia de 1ª escolha (Dor leve a moderada):</b> Dipirona Sódica 500 mg a 1 g VO de 6/6h por 24-48h, ou Paracetamol 750 mg VO de 6/6h.<br/>
    - <b>Analgesia preemptiva e Controle de Edema / Trismo (Cirurgias invasivas / Terceiros Molares):</b> Dexametasona 4 mg a 8 mg VO em dose única 1 hora antes da cirurgia + Analgésico de ação periférica no pós-operatório.<br/>
    - <b>Anti-inflamatórios Não Esteroidais (AINEs — uso restrito a 48-72h):</b> Ibuprofeno 400 mg a 600 mg VO de 8/8h, ou Nimesulida 100 mg VO de 12/12h.<br/>
    - <b>Antibioticoterapia em Infecções Odontogênicas Agudas (com sinais sistêmicos ou disseminação):</b> Amoxicilina 500 mg VO de 8/8h por 5 a 7 dias (dose de ataque opcional de 1 g). Em casos graves ou sem resposta em 48h, associar Metronidazol 400 mg de 8/8h ou utilizar Amoxicilina + Clavulanato de Potássio 875/125 mg de 12/12h.
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 7: CAPÍTULO 6 - ENDODONTIA CLÍNICA PASSO A PASSO (COHEN / LOPES & SIQUEIRA)
    story.append(Paragraph("Capítulo 6: Endodontia Clínica — Diagnóstico Pulpar e Passo a Passo do Tratamento de Canal (Cohen / Lopes & Siqueira)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    Segundo Hargreaves & Berman (Caminhos da Polpa - Cohen, 12ª ed.) e Lopes & Siqueira Jr. (Endodontia: Biologia e Técnica):<br/><br/>
    <b>1. Diagnóstico Pulpar e Periapical:</b><br/>
    - <b>Pulpite Reversível:</b> Dor provocada de curta duração (frio/doce) que cessa imediatamente após remoção do estímulo. Sem dor espontânea e percussão vertical negativa. Conduta: remoção do agente causal (cárie/restauração defeituosa) e restauração/proteção pulpar.<br/>
    - <b>Pulpite Irreversível Sintomática:</b> Dor espontânea, aguda, pulsátil, prolongada após estímulo térmico ao frio, podendo piorar em decúbito. Conduta: Tratamento endodôntico radical (Biopulpectomia). Em urgência: abertura coronária, remoção da polpa coronária/radicular, irrigação com NaOCl 2,5% e medicação intracanal com corticosteroide-antibiótico (Otosporin) ou Hidróxido de Cálcio.<br/>
    - <b>Necrose Pulpar:</b> Resposta negativa aos testes de sensibilidade pulpar ao frio (gás refrigerante propano/butano a -50°C). Conduta: Tratamento endodôntico de dentes despolpados (Necropulpectomia).<br/>
    - <b>Abscesso Perirradicular Agudo:</b> Dor espontânea intensa, localizada, sensação de "dente crescido" (extrusão), teste de percussão vertical intensamente positivo, tumefação intra ou extraoral e coleção purulenta. Conduta: Drenagem via canal (e incisão de flutuação em mucosa se houver ponto de flutuação submucoso), instrumentação, irrigação abundante, curativo de Hidróxido de Cálcio e antibioticoterapia sistêmica se houver febre, celulite, trismo ou linfadenopatia.<br/><br/>
    <b>2. Passo a Passo do Tratamento Endodôntico (Biopulpectomia e Necropulpectomia):</b><br/>
    - <b>Passo 1 (Radiografia, Anestesia e Isolamento Absoluto):</b> Radiografia periapical de diagnóstico, anestesia local, remoção de todo o tecido cariado e instalação obrigatória do isolamento absoluto com dique de borracha, arco de Ostby/Young e grampo específico, seguido de antissepsia do campo operatório com clorexidina 2% ou álcool iodado.<br/>
    - <b>Passo 2 (Acesso / Abertura Coronária e Esvaziamento):</b> Ponto de eleição na face palatina/lingual (anteriores) ou oclusal (posteriores), trepanação da câmara pulpar, remoção completa do teto da câmara com broca Endo-Z (sem tocar no assoalho) e desgaste compensatório para obtenção de acesso reto aos canais.<br/>
    - <b>Passo 3 (Exploração, Neutralização e Preparo Cervical/Médio — Crown-Down):</b> Irrigação da câmara com <b>Hipoclorito de Sódio (NaOCl 2,5% a 5,25%)</b>, exploração dos terços cervical e médio com limas manuais K #10 ou #15 (cateterismo) e alargamento cervical com brocas Gates-Glidden ou lima de Orifice Shaper.<br/>
    - <b>Passo 4 (Odontometria — Determinação do Comprimento Real de Trabalho - CRT):</b> Uso do localizador foraminal eletrônico até o forame apical (0.0) e recuo de <b>1,0 mm aquém do ápice</b> (limite CDC), confirmado por radiografia odontométrica.<br/>
    - <b>Passo 5 (Preparo Químico-Mecânico - PQM):</b> Instrumentação apical com sistemas rotatórios ou reciprocantes de Níquel-Titânio (NiTi) ou técnica escalonada manual, mantendo patência foraminal em casos de necrose e irrigação copiosa a cada troca de instrumento (mínimo 2 a 5 mL de NaOCl 2,5% por canal).<br/>
    - <b>Passo 6 (Remoção da Smear Layer e Agitação do Irrigante):</b> Irrigação final com <b>EDTA trissódico a 17% por 3 minutos</b> sob Agitação Ultrassônica Passiva (PUI - 3 ciclos de 20 segundos) para abertura dos túbulos dentinários, seguida de lavagem final com NaOCl e secagem com cones de papel absorvente estéreis.<br/>
    - <b>Passo 7 (Medicação Intracanal ou Obturação):</b> Em necropulpectomias com lesão ou falta de tempo hábil, aplica-se pasta de <b>Hidróxido de Cálcio P.A.</b> por 14 dias. Para obturação final: seleção e prova do cone principal de guta-percha (travamento apical, visual e radiográfico no CRT) + cimento endodôntico (resinoso epóxico como AH Plus ou biocerâmico) pela técnica de condensação lateral ativa ou termoplastificada, corte da guta-percha 2 mm abaixo do colo com calcador aquecido, limpeza com álcool e selamento coronário definitivo.
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 8: CAPÍTULO 7 - PERIODONTIA E IMPLANTODONTIA (LINDHE / AAP-EFP)
    story.append(Paragraph("Capítulo 7: Periodontia e Implantodontia — Classificação, Curetas Gracey e Terapia (Lindhe)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    Segundo Jan Lindhe & Niklaus P. Lang (Tratado de Periodontia Clínica e Implantologia Oral) e Workshop Mundial AAP/EFP (2018):<br/><br/>
    <b>1. Nova Classificação da Periodontite (Estágios e Graus — AAP/EFP):</b><br/>
    - <b>Estágio I (Periodontite Inicial):</b> Perda de inserção clínica interproximal (CAL) de 1 a 2 mm; perda óssea radiográfica restrita ao terço coronário (< 15%); profundidade de sondagem (PS) ≤ 4 mm; sem perda dentária.<br/>
    - <b>Estágio II (Periodontite Moderada):</b> CAL interproximal de 3 a 4 mm; perda óssea no terço coronário (15% a 33%); PS ≤ 5 mm; sem perda dentária por periodontite.<br/>
    - <b>Estágio III (Periodontite Severa com potencial de perda dentária adicional):</b> CAL ≥ 5 mm; perda óssea estendendo-se ao terço médio ou apical da raiz; PS ≥ 6 mm; lesão de furca Grau II ou III; perda de até 4 dentes por periodontite.<br/>
    - <b>Estágio IV (Periodontite Avançada com perda dentária extensa e colapso oclusal):</b> CAL ≥ 5 mm; perda de ≥ 5 dentes por periodontite; disfunção mastigatória, trauma oclusal secundário (mobilidade grau ≥ 2), colapso de mordida e menos de 20 dentes remanescentes (10 pares oponentes).<br/>
    - <b>Graus de Progressão:</b> <b>Grau A</b> (progressão lenta, não fumante, normoglicêmico); <b>Grau B</b> (progressão moderada, fumante < 10 cigarros/dia ou diabético com HbA1c < 7,0%); <b>Grau C</b> (progressão rápida, fumante ≥ 10 cigarros/dia ou diabético descompensado com HbA1c ≥ 7,0%).<br/><br/>
    <b>2. Passo a Passo da Terapia Básica Periodontal (Raspagem e Alisamento Radicular - RAR) e Numeração das Curetas de Gracey:</b><br/>
    - <b>Passo 1:</b> Sondagem periodontal completa em 6 sítios por dente, Índice de Placa Visível (IPV) e Sangramento Gengival (ISG), instrução de higiene oral individualizada (Técnica de Bass modificada + fio dental/escovas interdentais) e remoção de fatores retentivos de biofilme (excessos de restaurações, cavidades de cárie).<br/>
    - <b>Passo 2 (Instrumentação Supragengival e Subgengival):</b> Sob anestesia local por quadrante ou desinfecção de boca toda (Full-Mouth Disinfection), utiliza-se ultrassom piezoelétrico seguido de instrumentação manual com <b>Curetas Específicas de Gracey</b> (possuem apenas 1 borda cortante inclinada a 70° em relação à haste terminal):<br/>
      * <b>Curetas Gracey 1-2 e 3-4:</b> Todas as faces de dentes <b>anteriores</b> (incisivos e caninos).<br/>
      * <b>Curetas Gracey 5-6:</b> Todas as faces de dentes <b>anteriores e pré-molares</b>.<br/>
      * <b>Curetas Gracey 7-8 e 9-10:</b> Faces livres (<b>vestibular e lingual/palatina</b>) de dentes <b>posteriores</b>.<br/>
      * <b>Curetas Gracey 11-12:</b> Faces <b>mesiais</b> de dentes <b>posteriores</b> (pré-molares e molares).<br/>
      * <b>Curetas Gracey 13-14:</b> Faces <b>distais</b> de dentes <b>posteriores</b> (pré-molares e molares).<br/>
    - <b>Passo 3 (Reavaliação Periodontal):</b> Realizada <b>30 a 45 dias</b> após o término da RAR para maturação do epitélio juncional longo. Sítios com bolsas residuais ≥ 6 mm e sangramento à sondagem são indicados para retratamento ou acesso cirúrgico (retalho de Widman modificado). Em Periodontite Estágio III/IV Grau C generalizada, pode-se associar <b>Amoxicilina 500 mg + Metronidazol 400 mg de 8/8h por 7 dias</b> concomitantemente à RAR.<br/><br/>
    <b>3. Manejo das Doenças Peri-implantares (Mucosite vs Peri-implantite):</b><br/>
    - <b>Mucosite Peri-implantar:</b> Inflamação reversível dos tecidos moles peri-implantares (sangramento à sondagem suave) sem perda óssea além da remodelação inicial. Conduta: remoção mecânica profissional do biofilme (curetas de titânio/PEEK/teflon, jato de glicina/eritritol) associada a controle químico local (gel ou colutório de clorexidina 0,12% a 1% ou gel de clorexidina com xantana).<br/>
    - <b>Peri-implantite:</b> Sangramento/supuração à sondagem, aumento da profundidade de sondagem e perda óssea radiográfica progressiva. Conduta: terapia não cirúrgica inicial seguida de terapia cirúrgica (desbridamento a retalho aberto, descontaminação da superfície do implante e implantoplastia ou regeneração óssea guiada em defeitos infraósseos circunferenciais).
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 9: CAPÍTULO 8 - DENTÍSTICA RESTAURADORA, SISTEMAS ADESIVOS E PROTEÇÃO PULPAR (BARATIERI)
    story.append(Paragraph("Capítulo 8: Dentística Restauradora — Protocolo Adesivo, Resina Composta e Proteção Pulpar (Baratieri)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    Segundo Luiz Narciso Baratieri (Odontologia Restauradora: Fundamentos e Técnicas) e Kenneth J. Anusavice (Materiais Dentários):<br/><br/>
    <b>1. Passo a Passo de Restauração Direta em Resina Composta e Sistemas Adesivos:</b><br/>
    - <b>Passo 1 (Profilaxia, Seleção de Cor e Isolamento):</b> Profilaxia com pedra-pomes e água, seleção de cor com o dente hidratado sob luz natural, anestesia e isolamento absoluto (ou relativo rigoroso).<br/>
    - <b>Passo 2 (Preparo Cavitário e Remoção Seletiva de Tecido Cariado):</b> Acesso e remoção total da dentina infectada das paredes circundantes (junção amelodentinária limpa para selamento periférico). Na parede pulpar de cavidades profundas, preservar a dentina afetada passível de remineralização para evitar exposição pulpar.<br/>
    - <b>Passo 3 (Protocolo Adesivo Padrão-Ouro Atual — Condicionamento Ácido Seletivo em Esmalte):</b><br/>
      * <i>No Esmalte:</i> Aplicar <b>Ácido Fosfórico a 35-37% por 15 a 30 segundos exclusivamente nas margens de esmalte</b>, lavar abundantemente com spray água/ar por 30 segundos e secar.<br/>
      * <i>Na Dentina (com Adesivo Universal ou Autocondicionante de 2 passos como Clearfil SE Bond):</i> Não condicionar a dentina profunda com ácido fosfórico para evitar ativação de metaloproteinases (MMPs) e sensibilidade pós-operatória. Aplicar o primer/adesivo universal de forma <b>ativa (esfregando vigorosamente o microbrush por 20 segundos)</b>, evaporar o solvente com leve jato de ar por 5-10 segundos até a camada parar de se mover e fotopolimerizar por 20 segundos (irradiância ≥ 1.000 mW/cm²).<br/>
      * <i>Nota sobre Adesivos Convencionais (Condicionamento Ácido Total):</i> Se optar por condicionar esmalte (30s) e dentina (máximo 15s) com ácido fosfórico 37%, ao lavar deve-se proteger a dentina da desidratação (<b>Técnica Úmida</b> com bolinha de algodão ou papel absorvente), pois a secagem excessiva da dentina condicionada causa colapso da rede de fibras colágenas e falha da camada híbrida.<br/>
    - <b>Passo 4 (Inserção Incremental da Resina Composta):</b> Inserir incrementos oblíquos de no máximo <b>2 mm de espessura</b>, unindo no máximo duas paredes cavitárias por vez para minimizar o <b>Fator-C (Fator de Configuração Cavitária)</b> e a tensão de contração de polimerização. Fotopolimerizar cada incremento por 20 a 40 segundos.<br/>
    - <b>Passo 5 (Ajuste Oclusal, Acabamento e Polimento):</b> Checagem de contatos com carbono articular, acabamento com pontas diamantadas de granulação fina/extrafina (série F e FF), discos abrasivos (Sof-Lex) e borrachas espirais/pastas diamantadas.<br/><br/>
    <b>2. Protocolos de Proteção do Complexo Dentino-Pulpar por Profundidade da Cavidade:</b><br/>
    - <b>Cavidade Rasa ou Média (> 1,0 mm de dentina remanescente):</b> Apenas o Sistema Adesivo.<br/>
    - <b>Cavidade Profunda (0,5 a 1,0 mm de dentina remanescente, sem transparência rósea da polpa):</b> Forramento (liner) com <b>Cimento de Ionômero de Vidro (CIV)</b> modificado por resina + Sistema Adesivo + Resina Composta.<br/>
    - <b>Cavidade Muito Profunda (< 0,5 mm de dentina remanescente, risco de microexposição — Capeamento Pulpar Indireto):</b> Aplicação pontual na área mais profunda de <b>Cimento de Hidróxido de Cálcio</b> ou Biocerâmico (<b>MTA / Biodentine</b>) + camada protetora de <b>Cimento de Ionômero de Vidro</b> + Sistema Adesivo + Resina Composta.<br/>
    - <b>Exposição Pulpar Mecânica/Acidental Pequena em Polpa Saudável (Capeamento Pulpar Direto):</b> Hemostasia com soro fisiológico estéril ou hipoclorito de sódio, aplicação direta de <b>Hidróxido de Cálcio P.A. (pó/pasta)</b> ou <b>MTA / Biodentine</b> sobre a exposição + cobertura com CIV + restauração adesiva.
    """, normal_style))
    story.append(PageBreak())

    # PÁGINA 10: CAPÍTULO 9 - ESTOMATOLOGIA, BIÓPSIA E PATOLOGIA ORAL (NEVILLE)
    story.append(Paragraph("Capítulo 9: Estomatologia, Passo a Passo da Biópsia e Patologia Oral (Neville)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    Segundo Brad W. Neville et al. (Patologia Oral e Maxilofacial, 4ª ed.):<br/><br/>
    <b>1. Passo a Passo da Biópsia na Cavidade Oral (Incisional vs Excisional):</b><br/>
    - <b>Biópsia Excisional (Remoção Total):</b> Indicada para lesões clinicamente benignas, bem delimitadas e pequenas (geralmente <b>< 1,0 a 1,5 cm</b>), como hiperplasia fibrosa inflamatória, fibroma de irritação, papiloma escamoso e mucocele (na mucocele labial, deve-se remover também as glândulas salivares menores adjacentes na base para evitar recidiva).<br/>
    - <b>Biópsia Incisional (Remoção Parcial Representativa):</b> Indicada para lesões extensas (> 1,5 a 2,0 cm), lesões com suspeita de malignidade (ex: carcinoma espinocelular, leucoplasia não homogênea, eritroplasia), lesões de localização anatômica complexa ou doenças vesiculobolhosas/autoimunes (líquen plano, pênfigo, penfigoide).<br/>
    - <b>Passo a Passo Técnico da Biópsia Oral:</b><br/>
      1. Antissepsia com clorexidina 0,12% e anestesia local infiltrativa à distância das margens da lesão (nunca injetar anestésico diretamente dentro da lesão para não causar artefato histopatológico ou disseminação).<br/>
      2. Imobilização/tração suave da peça com fio de sutura transfixado na margem (evitar esmagar o fragmento com pinça dente de rato).<br/>
      3. Incisão elíptica em cunha ("em gomo de laranja") com lâmina de bisturi nº 15. Na biópsia incisional, incluir a área clinicamente mais suspeita e uma pequena margem de tecido normal periférico, evitando áreas centrais puramente necróticas.<br/>
      4. <b>Fixação imediata:</b> Mergulhar a peça imediatamente em frasco de boca larga contendo <b>Formol a 10% (formaldeído tamponado)</b> em volume no mínimo <b>10 a 20 vezes superior ao volume da peça</b>.<br/>
      5. Hemostasia, sutura com pontos simples (seda ou nylon 4-0) e envio ao laboratório de Patologia Bucal acompanhado de requisição clínica detalhada e exames de imagem.<br/><br/>
    <b>2. Cistos e Tumores Odontogênicos — Diagnóstico Diferencial Clássico (Neville):</b><br/>
    - <b>Cisto Radicular (Cisto Periapical):</b> O cisto odontogênico inflamatório mais comum dos maxilares (origem nos restos epiteliais de Malassez). Sempre associado ao ápice de um dente com <b>necrose pulpar</b> (teste de vitalidade negativo). Radiograficamente: lesão radiolúcida unilocular bem circunscrita no ápice radicular.<br/>
    - <b>Cisto Dentígero (Folicular):</b> O cisto odontogênico de desenvolvimento mais comum. Associado à coroa de um dente incluso/impactado (principalmente 3º molares inferiores e caninos superiores), inserindo-se tipicamente na <b>junção amelocementária (JAC)</b>.<br/>
    - <b>Ceratocisto Odontogênico:</b> Cisto de desenvolvimento com comportamento biológico agressivo e <b>alta taxa de recidiva (15% a 30%)</b>. Cresce no sentido anteroposterior pelos espaços medulares ósseos (principalmente corpo posterior e ramo da mandíbula) causando pouca expansão cortical inicial. Punção aspirativa revela líquido espesso branco-amarelado rico em queratina.<br/>
    - <b>Ameloblastoma:</b> Tumor odontogênico epitelial benigno, porém localmente invasivo e infiltrativo. Predileção pela região posterior da mandíbula (80%). Aspecto radiográfico clássico multilocular em <b>"bolhas de sabão" ou "favos de mel"</b>, frequentemente causando expansão das corticais vestibular e lingual e reabsorção radicular ("em lâmina de faca") dos dentes adjacentes.<br/>
    - <b>Odontoma (Composto vs Complexo):</b> O tumor odontogênico mais frequente (considerado hamartoma). O <b>Odontoma Composto</b> predomina na região anterior da maxila e apresenta múltiplas estruturas radiopacas semelhantes a pequenos dentículos. O <b>Odontoma Complexo</b> predomina na região posterior da mandíbula como uma massa radiopaca amorfa circundada por halo radiolúcido.
    """, normal_style))

    doc.build(story)
    return pdf_path

if __name__ == "__main__":
    from rag_engine import OdontoRAG
    path = generate_sample_pdf()
    print(f"Compêndio Padrão-Ouro gerado em: {path}")
    rag = OdontoRAG()
    chunks = rag.add_pdf(path)
    print(f"Indexação concluída! {chunks} trechos clínicos indexados no ChromaDB.")
