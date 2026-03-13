#!/usr/bin/env python3
"""
Young Stunners Invoice Generator
Professional invoice for Daniel Garcia YBTM Project
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime

def create_invoice():
    pdf_path = "/home/workspace/daniel-garcia-site/Young_Stunners_Invoice_YBTM_Project.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#8B0000'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        leading=14
    )
    
    small_style = ParagraphStyle(
        'SmallStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        leading=12
    )
    
    # Add Logo
    try:
        logo = Image('/home/workspace/daniel-garcia-site/young-stunners-logo.jpeg', width=2.5*inch, height=1.2*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    except:
        elements.append(Paragraph("YOUNG STUNNERS", title_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Company Info
    elements.append(Paragraph("Digital Marketing & Creative Solutions", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Invoice Header
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Invoice Details
    elements.append(Paragraph("Invoice #: <b>YS-2025-YBTM-001</b>", normal_style))
    elements.append(Paragraph("Date: <b>March 13, 2025</b>", normal_style))
    elements.append(Paragraph("Due Date: <b>March 27, 2025 (Net 14)</b>", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("Client: <b>Daniel Garcia / You Became The Money</b>", normal_style))
    elements.append(Paragraph("Project: <b>YBTM Website & Lead Magnet Package</b>", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Line separator
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#8B0000')))
    elements.append(Spacer(1, 0.2*inch))
    
    # Services Header
    elements.append(Paragraph("SERVICES PROVIDED", header_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Services Table
    services_data = [
        ['Service', 'Description', 'Amount'],
        [
            'Lead Magnet Ebook',
            '8-page illustrated PDF with custom chapter images\n"You Became The Money: The Path to Financial Sovereignty"\n(14 pages total with illustrations)',
            '$1,200.00'
        ],
        [
            'Website Enhancement',
            'Complete website update:\n• 8 books added to library\n• 8 Areas of Mastery\n• Testimonials section\n• Free ebook download integration',
            '$1,200.00'
        ],
        [
            'Voice Agent Knowledge Base',
            'Comprehensive documentation:\n• All 8 books detailed\n• Content style analysis\n• FAQ responses\n• Partner information',
            '$500.00'
        ],
        [
            'Domain Name Purchase',
            'youbecamethemoney.com\n(Registrar transfer included)',
            '$15.00'
        ],
        [
            '90-Day Support Package',
            'Unlimited edits & updates\nMarch 13, 2025 - June 13, 2025\nPriority response (24-48 hours)',
            '$585.00'
        ],
    ]
    
    services_table = Table(services_data, colWidths=[1.6*inch, 3.2*inch, 1.2*inch])
    services_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Body rows
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (2, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        
        # Grid
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#8B0000')),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#8B0000')),
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#8B0000')),
    ]))
    elements.append(services_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Total
    elements.append(Paragraph("TOTAL DUE: <b><font color='#8B0000' size='16'>$3,500.00</font></b>", 
                             ParagraphStyle('Total', parent=normal_style, alignment=TA_RIGHT, spaceBefore=10)))
    elements.append(Spacer(1, 0.3*inch))
    
    # Payment Terms
    elements.append(Paragraph("PAYMENT TERMS", header_style))
    elements.append(Spacer(1, 0.05*inch))
    elements.append(Paragraph("• 50% Deposit ($1,750.00) due upon invoice acceptance", normal_style))
    elements.append(Paragraph("• 50% Balance ($1,750.00) due upon project completion", normal_style))
    elements.append(Paragraph("• Payment Methods: Wire Transfer, PayPal, Crypto (USDC, BTC)", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Line separator before signature
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    elements.append(Spacer(1, 0.2*inch))
    
    # Authorization
    elements.append(Paragraph("AUTHORIZATION", header_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("By signing below, the Client acknowledges acceptance of this invoice and authorizes Young Stunners to proceed with the project as described.", small_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Signature lines
    elements.append(Paragraph("_" * 50, normal_style))
    elements.append(Paragraph("Client Signature", small_style))
    elements.append(Spacer(1, 0.05*inch))
    elements.append(Paragraph("Daniel Garcia", normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("_" * 20 + "     " + "_" * 20, normal_style))
    elements.append(Paragraph("Date                    Signature", small_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("Young Stunners | Digital Marketing & Creative Solutions", footer_style))
    elements.append(Paragraph("This invoice is valid for 14 days from the date of issue.", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    print(f"✓ Invoice created: {pdf_path}")
    print(f"✓ Total Amount: $3,500.00")
    print(f"✓ 90-Day Support: March 13, 2025 - June 13, 2025")
    print(f"✓ Logo: Young Stunners branding applied")
    print(f"✓ Signature line: Ready for Daniel Garcia")
    print(f"✓ Payment Terms: 50% deposit, 50% on completion")

if __name__ == "__main__":
    create_invoice()
