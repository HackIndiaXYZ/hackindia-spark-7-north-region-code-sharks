import uuid
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.graphics.shapes import Drawing, Rect

class BoxedParagraph(Flowable):
    def __init__(self, title, text, title_style, text_style, border_color, bg_color, width=6.5*inch):
        Flowable.__init__(self)
        self.width = width
        # Ensure newlines are preserved in the text by using <br/> tags
        text = text.replace('\n', '<br/>')
        self.title_p = Paragraph(title, title_style)
        self.text_p = Paragraph(text, text_style)
        self.border_color = colors.HexColor(border_color)
        self.bg_color = colors.HexColor(bg_color)
        self.padding = 12

    def wrap(self, availWidth, availHeight):
        self.title_w, self.title_h = self.title_p.wrap(self.width - 2 * self.padding, availHeight)
        self.text_w, self.text_h = self.text_p.wrap(self.width - 2 * self.padding, availHeight)
        self.height = self.title_h + self.text_h + 3 * self.padding
        return self.width, self.height

    def split(self, availWidth, availHeight):
        if availHeight < self.height:
            return []
        return [self]

    def draw(self):
        self.canv.saveState()
        # Draw background for title area
        self.canv.setFillColor(self.bg_color)
        self.canv.rect(0, self.height - self.title_h - 2 * self.padding, self.width, self.title_h + 2 * self.padding, fill=1, stroke=0)
        
        # Draw border
        self.canv.setStrokeColor(self.border_color)
        self.canv.setLineWidth(1.5)
        self.canv.rect(0, 0, self.width, self.height, fill=0, stroke=1)
        
        # Draw Title
        self.title_p.drawOn(self.canv, self.padding, self.height - self.title_h - self.padding)
        
        # Draw Content
        self.text_p.drawOn(self.canv, self.padding, self.padding)
        self.canv.restoreState()

def generate_clinical_pdf(user_info: dict, enzyme_profile: dict, drug_results: list, tech_note: str = None, lay_note: str = None) -> bytes:
    """
    Generates a professional PDF clinical report from user data,
    enzyme profile, and AI drug analysis results.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.white,
        alignment=1, # Center
        spaceAfter=20,
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#1f497d'),
        spaceBefore=15,
        spaceAfter=10,
    )
    
    normal_style = styles['Normal']
    
    drug_name_style = ParagraphStyle(
        'DrugName',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5,
    )
    
    Elements = []
    
    # --- 1. HEADER (Professional Blue Bar) ---
    header_data = [[Paragraph("<b>THE GENETIC GUARDRAIL</b>", title_style)]]
    header_table = Table(header_data, colWidths=[doc.width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1f497d')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    Elements.append(header_table)
    Elements.append(Spacer(1, 0.2 * inch))
    
    # --- 2. PATIENT INFORMATION ---
    Elements.append(Paragraph("Patient Information", heading_style))
    # Fallback user_id check
    analysis_id = user_info.get("analysis_id") or user_info.get("user_id") or str(uuid.uuid4())[:8].upper()
    
    patient_data = [
        ["Name:", user_info.get("name", "Unknown")],
        ["Email:", user_info.get("email", "Unknown")],
        ["Analysis ID:", analysis_id],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5 * inch, 4 * inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f497d')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    Elements.append(patient_table)
    Elements.append(Spacer(1, 0.2 * inch))
    
    # --- 3. GENOMIC METABOLIC PROFILE ---
    Elements.append(Paragraph("GENOMIC DNA BLUEPRINT", heading_style))
    Elements.append(Spacer(1, 0.2 * inch))

    Elements.append(Paragraph("Genomic Summary Table", heading_style))
    
    profile_data = [["Gene", "Phenotype"]]
    for gene, phenotype in enzyme_profile.items():
        profile_data.append([gene, phenotype])
        
    if len(profile_data) > 1:
        profile_table = Table(profile_data, colWidths=[2 * inch, 3.5 * inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        Elements.append(profile_table)
    else:
        Elements.append(Paragraph("No genomic profile data available.", normal_style))
        
    Elements.append(Spacer(1, 0.2 * inch))
    Elements.append(PageBreak())

    # --- 3.5 DNA BLUEPRINT (AI NARRATIVES) ---
    safe_fallback_technical = "Clinical data pending manual review."
    safe_fallback_layperson = "Clinical data pending manual review."

    # Map the narratives
    technical = tech_note or (user_info.get("summary", {}).get("technical_narrative") if isinstance(user_info.get("summary"), dict) else None)
    if not technical or "Error" in technical or technical == "Unable to generate technical summary.":
        technical = safe_fallback_technical
        
    layperson = lay_note or (user_info.get("summary", {}).get("layperson_summary") if isinstance(user_info.get("summary"), dict) else None)
    if not layperson or "Error" in layperson or layperson == "We couldn't generate a summary at this time; please consult your doctor.":
        layperson = safe_fallback_layperson

    # Custom styles for the narratives with professional font
    narrative_style = ParagraphStyle(
        'NarrativeStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.black,
    )

    # Helper function to create a bordered section
    def create_bordered_section(title, content, border_color, bg_color):
        return BoxedParagraph(title, content, heading_style, narrative_style, border_color, bg_color)

    Elements.append(create_bordered_section("Professional Clinical Interpretation", technical, '#1e3a8a', '#dbeafe')) # Blue
    Elements.append(Spacer(1, 0.3 * inch))
    Elements.append(create_bordered_section("Patient-Friendly Genomic Overview", layperson, '#166534', '#dcfce3')) # Green
    Elements.append(Spacer(1, 0.2 * inch))
    
    # Page Break for Medication Guardrail Analysis
    Elements.append(PageBreak())
    
    # --- 4. MEDICATION GUARDRAIL ANALYSIS ---
    Elements.append(Paragraph("Medication Guardrail Analysis", heading_style))
    
    if not drug_results:
        Elements.append(Paragraph("No medications analyzed.", normal_style))
        
    for drug in drug_results:
        # Drug Card
        drug_name = drug.get("drug_name", "Unknown Drug")
        risk_level = drug.get("risk_level", "Unknown")
        action = drug.get("action", "Unknown")
        clinical_note = drug.get("clinical_note", "No clinical notes available.")
        alternative = drug.get("alternative", None)
        toxicity_score = drug.get("toxicity_level", 0.0)
        
        # Color coding Risk Level & Action
        risk_color = colors.black
        action_upper = action.upper()
        if "AVOID" in action_upper or risk_level.upper() == "HIGH":
            risk_color = colors.red
        elif "ADJUST" in action_upper or risk_level.upper() == "MODERATE":
            risk_color = colors.orange
        elif "PRESCRIBE" in action_upper or risk_level.upper() == "LOW":
            risk_color = colors.green
            
        risk_style = ParagraphStyle(
            'RiskStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            textColor=risk_color,
        )
        
        Elements.append(Paragraph(f"<b>{drug_name}</b>", drug_name_style))
        Elements.append(Paragraph(f"Risk Level: {risk_level} | Action: {action}", risk_style))
        
        if alternative and str(alternative).strip() and str(alternative).lower() != "none":
            Elements.append(Paragraph(f"<b>Alternative:</b> {alternative}", normal_style))
            
        Elements.append(Spacer(1, 0.05 * inch))
        Elements.append(Paragraph(f"<b>AI Clinical Guidance:</b> {clinical_note}", normal_style))
        
        # Toxicity Gauge Visual
        Elements.append(Spacer(1, 0.05 * inch))
        Elements.append(Paragraph("<b>Toxicity Gauge:</b>", normal_style))
        
        d = Drawing(400, 20)
        # Background bar
        bg_bar = Rect(0, 5, 300, 10, fillColor=colors.HexColor('#e0e0e0'), strokeColor=None)
        d.add(bg_bar)
        # Fill bar
        fill_width = 300 * max(0, min(1, toxicity_score / 100.0))
        if toxicity_score > 70:
            bar_color = colors.red
        elif toxicity_score > 30:
            bar_color = colors.orange
        else:
            bar_color = colors.green
        fill_bar = Rect(0, 5, fill_width, 10, fillColor=bar_color, strokeColor=None)
        d.add(fill_bar)
        
        Elements.append(d)
        Elements.append(Spacer(1, 0.15 * inch))
        
        # Divider
        Elements.append(Table([['']], colWidths=[doc.width], style=[
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        Elements.append(Spacer(1, 0.1 * inch))

    # --- 5. FOOTER (Disclaimer) ---
    Elements.append(Spacer(1, 0.3 * inch))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.gray,
        alignment=1 # Center
    )
    disclaimer_text = "Disclaimer: This report is generated by an AI-driven Pharmacogenomic Orchestrator. Consult a licensed physician before altering medications."
    Elements.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build PDF
    doc.build(Elements)
    
    return buffer.getvalue()
