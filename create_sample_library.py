import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from rag_engine import OdontoRAG, DOCUMENTS_PATH

pdf_filename = "Manual_Diretrizes_Clinicas_Odontologia_Exemplo.pdf"
pdf_path = os.path.join(DOCUMENTS_PATH, pdf_filename)

def generate_sample_pdf():
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    story = []
    
    # Capa / Título
    story.append(Paragraph("Manual de Condutas Clínicas e Farmacologia em Odontologia", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Organização:</b> Diretrizes Odontológicas Baseadas em Evidências para Ensino e TCC", normal_style))
    story.append(Paragraph("<b>Referências Base:</b> Malamed (Anestesiologia Local), Diretrizes AHA/CFO (Profilaxia Infecciosa), Farmacologia Clínica Odontológica (Wannmacher)", normal_style))
    story.append(Spacer(1, 20))
    story.append(PageBreak())
    
    # Página 2: Anestesiologia e Doses Máximas (Malamed)
    story.append(Paragraph("Capítulo 1: Anestésicos Locais em Odontologia — Dosagens e Segurança", heading_style))
    story.append(Spacer(1, 10))
    p1 = """
    Segundo Stanley F. Malamed (Manual de Anestesia Local):<br/><br/>
    <b>1. Cloridrato de Lidocaína 2% com Epinefrina 1:100.000:</b><br/>
    - É o anestésico padrão-ouro em odontologia mundial.<br/>
    - Dose máxima recomendada por peso corpóreo: <b>4,4 mg/kg</b> (não devendo ultrapassar o teto máximo absoluto de <b>300 mg</b> por sessão clínica em pacientes adultos hígidos).<br/>
    - Cada tubete de 1,8 mL de lidocaína 2% contém exatamente <b>36 mg</b> de sal anestésico e 0,018 mg de epinefrina.<br/>
    - Portanto, o número máximo de tubetes de lidocaína 2% com epinefrina 1:100.000 para um adulto hígido de 70 kg é de aproximadamente <b>8 tubetes</b> (300 mg / 36 mg ≈ 8,3 tubetes).<br/><br/>
    <b>2. Articaína 4% com Epinefrina 1:100.000 ou 1:200.000:</b><br/>
    - Dose máxima recomendada: <b>7,0 mg/kg</b> (teto máximo de 500 mg). Cada tubete de 1,8 mL contém 72 mg de articaína.<br/>
    - Excelente difusibilidade óssea, muito utilizada em mandíbula e molares inferiores para infiltração, mas com maior risco de parestesia quando usada em bloqueio do nervo alveolar inferior.<br/><br/>
    <b>3. Mepivacaína 3% sem vasoconstritor:</b><br/>
    - Dose máxima recomendada: <b>4,4 mg/kg</b> (teto de 300 mg). Cada tubete contém 54 mg.<br/>
    - Indicada para procedimentos curtos ou quando há contraindicação absoluta ao uso de vasoconstritores adrenérgicos.<br/>
    """
    story.append(Paragraph(p1, normal_style))
    story.append(PageBreak())
    
    # Página 3: Atendimento a Gestantes
    story.append(Paragraph("Capítulo 2: Protocolo Odontológico para Atendimento de Pacientes Gestantes", heading_style))
    story.append(Spacer(1, 10))
    p2 = """
    Diretrizes clínicas para atendimento de gestantes na clínica odontológica:<br/><br/>
    <b>1. Período Mais Seguro:</b><br/>
    - O <b>segundo trimestre gestacional (da 14ª à 27ª semana)</b> é o momento eletivo ideal para a realização de procedimentos clínicos essenciais, restaurações, profilaxias e cirurgias inadiáveis, pois a organogênese do feto já está completa e o útero ainda não comprime excessivamente a veia cava inferior.<br/><br/>
    <b>2. Escolha do Anestésico Local:</b><br/>
    - Anestésico de escolha: <b>Lidocaína a 2% com epinefrina 1:100.000</b> (ambos classificados na <b>Categoria B da FDA</b>).<br/>
    - O uso de epinefrina nesta concentração é seguro, devendo-se utilizar técnica com aspiração prévia negativa e velocidade lenta de injeção, limitando a no máximo 2 a 3 tubetes por atendimento.<br/>
    - <b>Contraindicações expressas:</b> Prilocaína com felipressina (a felipressina pode induzir contrações uterinas devido ao efeito análogo à ocitocina; risco de meta-hemoglobinemia) e Articaína/Bupivacaína (Categoria C da FDA).<br/><br/>
    <b>3. Posição na Cadeira Odontológica:</b><br/>
    - Evitar posição supina dorsal prolongada devido à Síndrome da Hipotensão Supina (compressão da veia cava inferior pelo útero gravídico). Recomenda-se inclinar a paciente ligeiramente para o lado esquerdo (decúbito lateral esquerdo de 15 graus com apoio de almofada no flanco direito).<br/>
    """
    story.append(Paragraph(p2, normal_style))
    story.append(PageBreak())

    # Página 4: Profilaxia Antibiótica para Endocardite Infecciosa (AHA / SBC / CFO)
    story.append(Paragraph("Capítulo 3: Profilaxia Antibiótica da Endocardite Infecciosa em Odontologia", heading_style))
    story.append(Spacer(1, 10))
    p3 = """
    De acordo com as diretrizes atualizadas da American Heart Association (AHA) e Conselho Federal de Odontologia (CFO):<br/><br/>
    <b>1. Pacientes de Alto Risco com Indicação Formal:</b><br/>
    - Portadores de prótese valvar cardíaca mecânica ou biológica.<br/>
    - Pacientes com histórico prévio documentado de endocardite infecciosa.<br/>
    - Cardiopatias congênitas cianóticas não corrigidas ou corrigidas com material protético nos últimos 6 meses.<br/>
    - Receptores de transplante cardíaco que desenvolveram valvopatia.<br/>
    <i>Nota: Prolapso de valva mitral sem regurgitação e sopros funcionais NÃO possuem mais indicação de profilaxia.</i><br/><br/>
    <b>2. Procedimentos Odontológicos que Exigem Profilaxia:</b><br/>
    - Procedimentos que envolvam manipulação de tecido gengival, região periapical dentária ou perfuração da mucosa oral (exodontias, raspagem subgengival, biópsias, cirurgias periapicais, instalação de implantes).<br/><br/>
    <b>3. Esquema Posológico Recomendado (Dose Única 30 a 60 minutos antes do procedimento):</b><br/>
    - <b>Primeira Escolha (Via Oral em Adultos):</b> Amoxicilina <b>2 g</b> por via oral em dose única.<br/>
    - <b>Primeira Escolha (Crianças):</b> Amoxicilina <b>50 mg/kg</b> por via oral em dose única (máximo 2 g).<br/>
    - <b>Pacientes Alérgicos a Penicilinas / Betalactâmicos (Adultos):</b><br/>
      * Azitromicina <b>500 mg</b> por via oral em dose única.<br/>
      * Claritromicina <b>500 mg</b> por via oral em dose única.<br/>
      * Cefalexina <b>2 g</b> por via oral (somente se a alergia à penicilina não foi do tipo anafilática imediata).<br/>
      <i>Atenção: A Clindamicina NÃO é mais recomendada pela AHA devido ao risco elevado de colite pseudomembranosa por Clostridioides difficile.</i><br/>
    """
    story.append(Paragraph(p3, normal_style))
    
    doc.build(story)
    print(f"PDF de referência odontológica gerado com sucesso em: {pdf_path}")

if __name__ == "__main__":
    generate_sample_pdf()
    print("Indexando o documento no banco vetorial ChromaDB...")
    rag = OdontoRAG()
    chunks = rag.add_pdf(pdf_path)
    print(f"Indexação concluída! {chunks} trechos foram adicionados ao ChromaDB.")
