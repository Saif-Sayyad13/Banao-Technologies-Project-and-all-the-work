"""Turns memo-to-ritu.md into a one-page PDF.  python memo/build_pdf.py"""
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

md = open('memo/memo-to-ritu.md').read().split('\n')
ss = getSampleStyleSheet()
B = ParagraphStyle('b', parent=ss['BodyText'], fontName='Helvetica', fontSize=10, leading=13, spaceAfter=3)
H = ParagraphStyle('h', parent=B, fontName='Helvetica-Bold', fontSize=12, leading=14, spaceBefore=7, spaceAfter=2, textColor=colors.HexColor('#1f3a8a'))
T = ParagraphStyle('t', parent=B, fontSize=9, leading=11, spaceAfter=0)
fmt = lambda s: re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s.replace('&', '&amp;').replace('<', '&lt;'))
story, items, i = [], [], 0
doc = SimpleDocTemplate('memo/memo-to-ritu.pdf', pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=12*mm, bottomMargin=10*mm, title='Memo to Ritu', author='Saif Sayyad')

def flush():
    global items
    if items:
        story.append(ListFlowable([ListItem(Paragraph(fmt(t), B), leftIndent=14) for t in items], bulletType='1', leftIndent=14, bulletFontSize=10))
        items = []

while i < len(md):
    l = md[i]
    if l.startswith('## '):
        flush(); story.append(Paragraph(fmt(l[3:]), H))
    elif l.startswith('|'):
        rows = []
        while i < len(md) and md[i].startswith('|'):
            if not set(md[i]) <= set('|- '):
                rows.append([Paragraph(fmt(c.strip()), T) for c in md[i].strip('|').split('|')])
            i += 1
        t = Table(rows, colWidths=[44*mm, 52*mm, 22*mm, 32*mm, 32*mm])
        t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), .4, colors.grey), ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8edf8')),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        story += [t, Spacer(1, 4)]
        continue
    elif re.match(r'\d\. ', l):
        items.append(l[3:])
    elif l.strip():
        flush(); story.append(Paragraph(fmt(l), B))
    i += 1
flush(); doc.build(story)
from pypdf import PdfReader
print('pages:', len(PdfReader('memo/memo-to-ritu.pdf').pages))
