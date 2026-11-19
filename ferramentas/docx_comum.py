"""Funções comuns aos documentos Word da Recorrida (python-docx)."""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
APP = Path.home() / "Library/CloudStorage/OneDrive-Pessoal/GPTs e bots/Aplicativos/Recorrida app"
MARROM = RGBColor(0x4A, 0x28, 0x14)
TERRA = RGBColor(0x8C, 0x4A, 0x22)
CINZA = RGBColor(0x55, 0x55, 0x55)
FONTE = "Arial"


def novo_documento(titulo_doc: str) -> Document:
    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)
    st = doc.styles
    st["Normal"].font.name = FONTE
    st["Normal"].font.size = Pt(10.5)
    st["Normal"].element.rPr.rFonts.set(qn("w:eastAsia"), FONTE)
    st["Normal"].paragraph_format.space_after = Pt(4)
    for nome, tam, cor, antes in (("Title", 22, MARROM, 0), ("Heading 1", 15, MARROM, 16), ("Heading 2", 12, TERRA, 10)):
        s = st[nome]
        s.font.name, s.font.size, s.font.bold, s.font.color.rgb = FONTE, Pt(tam), True, cor
        rf = s.element.rPr.find(qn("w:rFonts"))
        if rf is not None:
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                rf.attrib.pop(qn(a), None)
            rf.set(qn("w:ascii"), FONTE); rf.set(qn("w:hAnsi"), FONTE)
        s.paragraph_format.space_before = Pt(antes)
        s.paragraph_format.space_after = Pt(6)
        s.paragraph_format.keep_with_next = True
    for nome in ("List Bullet", "List Number"):
        st[nome].font.name = FONTE
        st[nome].paragraph_format.space_after = Pt(2)
    doc.core_properties.title = titulo_doc
    # rodapé com número da página
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(titulo_doc + "  ·  página ")
    r.font.size, r.font.color.rgb = Pt(8), CINZA
    campo(p, "PAGE")
    return doc


def campo(par, codigo):
    r = par.add_run()
    r.font.size = Pt(8)
    for tipo, txt in (("begin", None), (None, codigo), ("end", None)):
        if tipo:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tipo); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)


def par(doc, texto="", negrito_ini=None, estilo=None, cor=None, tam=None, italico=False):
    """Parágrafo; trechos entre ** ficam em negrito."""
    p = doc.add_paragraph(style=estilo)
    partes = texto.split("**")
    for i, t in enumerate(partes):
        if not t:
            continue
        r = p.add_run(t)
        r.bold = i % 2 == 1
        r.italic = italico
        if cor is not None:
            r.font.color.rgb = cor
        if tam:
            r.font.size = Pt(tam)
    return p


def lista(doc, itens, numerada=False):
    """Lista com marcadores ou numerada (a numeração recomeça em 1 em cada lista)."""
    for i, t in enumerate(itens, 1):
        if numerada:
            p = par(doc, f"{i}.\t" + t)
            p.paragraph_format.left_indent = Cm(0.7)
            p.paragraph_format.first_line_indent = Cm(-0.7)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(0.7))
            p.paragraph_format.space_after = Pt(2)
        else:
            par(doc, t, estilo="List Bullet")


def checklist(doc, itens):
    for t in itens:
        p = par(doc, "☐  " + t)
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)


def sombrear(celula, cor_hex):
    tc = celula._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), cor_hex)
    tc.append(sh)


def tabela(doc, cabecalho, linhas, larguras_cm):
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(cabecalho):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = MARROM
        sombrear(c, "F1ECE4")
    for linha in linhas:
        cels = t.add_row().cells
        for i, v in enumerate(linha):
            cels[i].text = ""
            p = cels[i].paragraphs[0]
            for j, trecho in enumerate(str(v).split("**")):
                if trecho:
                    p.add_run(trecho).bold = j % 2 == 1
    for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), larguras_cm):  # larguras também na grade (LibreOffice/Quick Look)
        gc.set(qn("w:w"), str(int(Cm(w).twips)))
    for row in t.rows:
        for i, w in enumerate(larguras_cm):
            row.cells[i].width = Cm(w)
            for p in row.cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for r in p.runs:
                    r.font.size = Pt(9.5)
    doc.add_paragraph()
    return t


def caixa(doc, texto, cor_hex="FFF6CC"):
    """Aviso em destaque (tabela de 1 célula)."""
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    c.width = Cm(16.6)
    sombrear(c, cor_hex)
    c.text = ""
    p = c.paragraphs[0]
    for j, trecho in enumerate(texto.split("**")):
        if trecho:
            p.add_run(trecho).bold = j % 2 == 1
    doc.add_paragraph()


def link(par_, url, texto=None):
    """Hiperlink clicável."""
    parte = par_.part
    rid = parte.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    cor = OxmlElement("w:color"); cor.set(qn("w:val"), "1F5FA8"); rpr.append(cor)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = texto or url; t.set(qn("xml:space"), "preserve"); r.append(t)
    h.append(r)
    par_._p.append(h)


def salvar(doc, destino: Path):
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc.save(destino)
    print("Gerado:", destino)
