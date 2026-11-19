#!/usr/bin/env python3
"""
Recorrida — gera a planilha de cadastro que o responsável da propriedade preenche.

Uso:  python3 ferramentas/gerar_cadastro.py [arquivo.xlsx]
Padrão: "Recorrida app/Implantacao/Cadastro-propriedade-Recorrida.xlsx" (OneDrive).

As abas seguem o formato lido por importarCadastro (apps-script/Cadastro.gs):
linha 1 = título, linha 2 = cabeçalho, linha 3 = exemplo (cinza), dados a partir da linha 4.
Na aba Propriedade: Campo | Resposta | Orientação, a partir da linha 3.
"""
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

PADRAO = (Path.home() / "Library/CloudStorage/OneDrive-Pessoal/GPTs e bots/Aplicativos/Recorrida app"
          / "Implantacao/Cadastro-propriedade-Recorrida.xlsx")

MARROM = "4A2814"
CREME = "F1ECE4"
AMARELO = "FFF6CC"   # célula para preencher
CINZA = "8A8A8A"
F = "Arial"
borda = Border(*(Side(style="thin", color="D9D2C5"),) * 4)
LINHAS_DADOS = 150  # linhas com formatação e listas suspensas

TIPOS_MEDICAMENTO = ["Vermífugo", "Carrapaticida", "Endectocida", "Antibiótico", "Anti-inflamatório",
                     "Vacina clostridiose", "Vacina reprodutiva", "Vacina", "Suplemento injetável", "Outro"]
ESPECIES = ["Bov", "Ovino", "Equino", "Caprino"]


def titulo(ws, texto, sub, ncol):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    c = ws.cell(1, 1, f"{texto}  —  {sub}")
    c.font = Font(name=F, size=12, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=MARROM)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[1].height = 42


def cabecalho(ws, linha, nomes, larguras):
    for i, (n, w) in enumerate(zip(nomes, larguras), 1):
        c = ws.cell(linha, i, n)
        c.font = Font(name=F, bold=True, color=MARROM)
        c.fill = PatternFill("solid", fgColor=CREME)
        c.border = borda
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = w
    ws.row_dimensions[linha].height = 30


def exemplo(ws, linha, valores):
    for i, v in enumerate(valores, 1):
        c = ws.cell(linha, i, v)
        c.font = Font(name=F, italic=True, color=CINZA)
        c.border = borda
    ws.cell(linha, 1).comment = Comment("Linha de EXEMPLO: não é importada. Preencha a partir da linha de baixo.", "Recorrida")


def area_dados(ws, ncol, ini=4, preenchidas=()):
    for r in range(ini, ini + LINHAS_DADOS):
        for col in range(1, ncol + 1):
            c = ws.cell(r, col)
            c.font = Font(name=F)
            c.border = borda
            c.fill = PatternFill("solid", fgColor=AMARELO)
    for r, linha in enumerate(preenchidas, ini):
        for col, v in enumerate(linha, 1):
            ws.cell(r, col, v)


def lista(ws, intervalo, opcoes, msg, permitir_outro=False):
    dv = DataValidation(type="list", formula1='"' + ",".join(opcoes) + '"', allow_blank=True,
                        showErrorMessage=not permitir_outro, errorStyle="warning" if permitir_outro else "stop",
                        promptTitle="Escolha", prompt=msg, showInputMessage=True)
    dv.error = "Escolha um valor da lista."
    ws.add_data_validation(dv)
    dv.add(intervalo)


def montar(destino: Path):
    wb = Workbook()

    # ------------------------------------------------------------ Instruções
    ws = wb.active
    ws.title = "Instruções"
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 110
    textos = [
        ("Recorrida — cadastro da propriedade", "t"),
        ("Esta planilha reúne o que é preciso para criar o aplicativo Recorrida da sua propriedade. "
         "Preencha as abas e devolva o arquivo por e-mail ou WhatsApp.", ""),
        ("", ""),
        ("Como preencher", "h"),
        ("• Escreva só nas células AMARELAS. A linha cinza em itálico de cada aba é um exemplo e não é importada.", ""),
        ("• Propriedade: dados gerais e como o app deve funcionar.", ""),
        ("• Usuários: quem vai usar o app. Cada pessoa precisa de um e-mail Google (Gmail ou e-mail da empresa no Google). "
         "Em \"Acesso\", escolha \"Só o app\" ou \"App e planilha\" (quem também vê e edita a planilha Google com todos os dados).", ""),
        ("• Potreiros: todos os potreiros/piquetes com o nome que a equipe usa no campo. "
         "Em \"Nomes alternativos\", outros jeitos de chamar o mesmo potreiro, separados por ponto e vírgula.", ""),
        ("• Categorias: já vem com uma sugestão. Apague o que não usa, corrija os nomes e acrescente o que faltar. "
         "A coluna \"Ordem no app\" define a ordem em que as categorias aparecem no app (1 = primeira).", ""),
        ("• Minerais: os produtos colocados no cocho e quantos kg tem cada saco.", ""),
        ("• Medicamentos: os produtos usados no rebanho, o tipo e a unidade da dose.", ""),
        ("", ""),
        ("Imagens (opcional)", "h"),
        ("Mande em separado, por e-mail ou WhatsApp, os arquivos originais (não print de tela):", ""),
        ("• Logo ou marca da propriedade, de preferência com fundo transparente (PNG ou SVG).", ""),
        ("• Uma foto horizontal da propriedade (fundo do topo do app) e, se quiser, outra vertical (tela de entrada).", ""),
        ("Sem imagens, o app usa as imagens padrão da Recorrida. Elas podem ser trocadas depois.", ""),
        ("", ""),
        ("Depois de pronto", "h"),
        ("Você recebe um documento com o link do app, o link da planilha Google com os dados e o passo a passo "
         "para instalar o app no iPhone e no Android.", ""),
        ("", ""),
        ("Legenda", "h"),
        ("Células amarelas: para preencher", "amarelo"),
        ("Linha cinza em itálico: exemplo (não é importada)", "exemplo"),
    ]
    for i, (t, est) in enumerate(textos, 2):
        c = ws.cell(i, 2, t)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.font = Font(name=F, size=11)
        if est == "t":
            c.font = Font(name=F, size=16, bold=True, color=MARROM)
            ws.row_dimensions[i].height = 28
        elif est == "h":
            c.font = Font(name=F, size=12, bold=True, color=MARROM)
        elif est == "amarelo":
            c.fill = PatternFill("solid", fgColor=AMARELO); c.border = borda
        elif est == "exemplo":
            c.font = Font(name=F, italic=True, color=CINZA); c.border = borda
        if len(t) > 110:
            ws.row_dimensions[i].height = 30

    # ------------------------------------------------------------ Propriedade
    ws = wb.create_sheet("Propriedade")
    titulo(ws, "Propriedade", "dados gerais e como o app deve funcionar (preencha a coluna Resposta)", 3)
    cabecalho(ws, 2, ["Campo", "Resposta", "Orientação"], [38, 42, 78])
    campos = [
        ("Nome completo da propriedade", "", "Como deve aparecer no app. Ex.: Fazenda Sanga dos Touros."),
        ("Nome curto", "", "Aparece no topo do app. Ex.: Sanga dos Touros."),
        ("Nome do ícone (até 12 letras)", "", "Nome embaixo do ícone no celular. Ex.: Sanga Touros."),
        ("Município / UF", "", ""),
        ("Responsável pelo app", "", "Quem responde pelas informações e libera novos usuários."),
        ("Telefone / WhatsApp do responsável", "", ""),
        ("E-mail Google do responsável", "", "Recebe o acesso à planilha Google com os dados."),
        ("Movimentação opcional (SIM/NÃO)", "NÃO",
         "NÃO: quando a contagem de animais muda, o app já abre o quadro \"O que aconteceu?\" "
         "(morte, venda, transferência, nascimento...). SIM: o quadro só abre se a pessoa ligar "
         "\"Registrar o que mudou\"; sem isso, salva só a contagem. Na dúvida, comece com SIM "
         "se a equipe tem pouca prática com celular. Pode ser trocado depois."),
        ("Vai enviar logo/marca? (SIM/NÃO)", "", "Mande o arquivo em separado (veja Instruções)."),
        ("Vai enviar fotos? (SIM/NÃO)", "", "Mande os arquivos em separado (veja Instruções)."),
        ("Espécies na propriedade", "", "Ex.: Bovinos e ovinos."),
        ("Observações", "", "Qualquer coisa que ajude a montar o app."),
    ]
    for r, (campo, resp, ori) in enumerate(campos, 3):
        a = ws.cell(r, 1, campo); a.font = Font(name=F, bold=True); a.border = borda
        a.alignment = Alignment(vertical="top", wrap_text=True)
        b = ws.cell(r, 2, resp or None); b.font = Font(name=F); b.border = borda
        b.fill = PatternFill("solid", fgColor=AMARELO); b.alignment = Alignment(vertical="top", wrap_text=True)
        c = ws.cell(r, 3, ori); c.font = Font(name=F, size=9, color="555555"); c.border = borda
        c.alignment = Alignment(vertical="top", wrap_text=True)
        ws.row_dimensions[r].height = 30 if len(ori) < 95 else 15 * (len(ori) // 80 + 1)
    for r, (campo, _, _) in enumerate(campos, 3):
        if "(SIM/NÃO)" in campo or "? (SIM/NÃO)" in campo:
            lista(ws, f"B{r}", ["SIM", "NÃO"], "SIM ou NÃO")
    ws.freeze_panes = "A3"

    # ------------------------------------------------------------ Usuários
    ws = wb.create_sheet("Usuários")
    titulo(ws, "Usuários", "quem vai usar o app; cada pessoa precisa de um e-mail Google", 5)
    cabecalho(ws, 2, ["Nome", "E-mail Google (Gmail)", "Função", "Acesso", "Ativo (SIM/NÃO)"],
              [30, 36, 22, 20, 14])
    exemplo(ws, 3, ["João da Silva", "joao.silva@gmail.com", "Campo", "Só o app", "SIM"])
    area_dados(ws, 5)
    fim = 3 + LINHAS_DADOS
    lista(ws, f"C4:C{fim}", ["Administrador", "Gerente", "Campo", "Consulta"], "Função (pode digitar outra)", permitir_outro=True)
    lista(ws, f"D4:D{fim}", ["Só o app", "App e planilha"],
          "Só o app: usa o app no celular. App e planilha: também recebe a planilha Google com todos os dados")
    lista(ws, f"E4:E{fim}", ["SIM", "NÃO"], "NÃO: a pessoa fica bloqueada no app")
    dv = DataValidation(type="custom", formula1='AND(ISNUMBER(SEARCH("@",B4)),ISNUMBER(SEARCH(".",B4)),ISERROR(SEARCH(" ",B4)))',
                        allow_blank=True, showErrorMessage=True, errorTitle="E-mail inválido",
                        error="Digite um e-mail completo, sem espaços (ex.: nome@gmail.com).")
    ws.add_data_validation(dv); dv.add(f"B4:B{fim}")
    ws.freeze_panes = "A4"

    # ------------------------------------------------------------ Potreiros
    ws = wb.create_sheet("Potreiros")
    titulo(ws, "Potreiros", "todos os potreiros/piquetes, com o nome usado no campo", 4)
    cabecalho(ws, 2, ["Potreiro", "Nomes alternativos (separe com ;)", "Área (ha, opcional)", "Observações"], [32, 40, 16, 40])
    exemplo(ws, 3, ["Banhado do Fundo", "banhado fundo; fundão", 42, "tem açude"])
    area_dados(ws, 4)
    ws.freeze_panes = "A4"

    # ------------------------------------------------------------ Categorias
    ws = wb.create_sheet("Categorias")
    titulo(ws, "Categorias", "sugestão já preenchida: apague o que não usa e acrescente o que faltar; "
                             "\"Ordem no app\" é a ordem em que aparecem no app", 4)
    cabecalho(ws, 2, ["Ordem no app", "Espécie", "Categoria", "Nomes alternativos (separe com ;)"], [12, 14, 30, 44])
    exemplo(ws, 3, [1, "Bov", "Vacas de invernar", "vaca gorda; invernar"])
    area_dados(ws, 4, preenchidas=[(i,) + t for i, t in enumerate([
        ("Bov", "Vacas", "vaca; vc"), ("Bov", "Vacas com cria", "vaca com cria; vc com cria"),
        ("Bov", "Novilhas", "vaquilhona; vq"), ("Bov", "Novilhos", "boi; bois"),
        ("Bov", "Terneiros", "ternero; terneira"), ("Bov", "Touros", "touro; toro"),
        ("Ovino", "Ovelhas", ""), ("Ovino", "Cordeiros", ""), ("Ovino", "Borregas", ""), ("Ovino", "Carneiros", ""),
    ], 1)])
    lista(ws, f"B4:B{3 + LINHAS_DADOS}", ESPECIES, "Bov, Ovino, Equino ou Caprino")
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="999", allow_blank=True,
                        showErrorMessage=True, error="Digite um número inteiro (1 = primeira no app).")
    ws.add_data_validation(dv); dv.add(f"A4:A{3 + LINHAS_DADOS}")
    ws.freeze_panes = "A4"

    # ------------------------------------------------------------ Minerais
    ws = wb.create_sheet("Minerais")
    titulo(ws, "Minerais", "produtos colocados no cocho", 3)
    cabecalho(ws, 2, ["Mineral", "Kg por saco", "Nomes alternativos (separe com ;)"], [34, 14, 44])
    exemplo(ws, 3, ["Proteico 30 M", 30, "proteico; P30"])
    area_dados(ws, 3)
    dv = DataValidation(type="decimal", operator="between", formula1="0", formula2="1000", allow_blank=True,
                        showErrorMessage=True, error="Digite só o número de kg (ex.: 30).")
    ws.add_data_validation(dv); dv.add(f"B4:B{3 + LINHAS_DADOS}")
    ws.freeze_panes = "A4"

    # ------------------------------------------------------------ Medicamentos
    ws = wb.create_sheet("Medicamentos")
    titulo(ws, "Medicamentos", "produtos usados no rebanho", 4)
    cabecalho(ws, 2, ["Medicamento", "Tipo", "Unidade da dose", "Nomes alternativos (separe com ;)"], [34, 24, 16, 40])
    exemplo(ws, 3, ["Ivomec", "Endectocida", "mL", "ivermectina"])
    area_dados(ws, 4)
    lista(ws, f"B4:B{3 + LINHAS_DADOS}", TIPOS_MEDICAMENTO, "Tipo do medicamento (pode digitar outro)", permitir_outro=True)
    lista(ws, f"C4:C{3 + LINHAS_DADOS}", ["mL", "g", "dose", "comprimido", "bisnaga"], "Unidade (pode digitar outra)", permitir_outro=True)
    ws.freeze_panes = "A4"

    for w in wb.worksheets:
        w.sheet_properties.tabColor = MARROM if w.title in ("Instruções", "Propriedade") else "C9A66B"
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)
    print("Gerado:", destino)


if __name__ == "__main__":
    montar(Path(sys.argv[1]) if len(sys.argv) > 1 else PADRAO)
