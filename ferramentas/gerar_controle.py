# /// script
# dependencies = ["python-docx"]
# ///
"""
Recorrida — CONTROLE da implantação de uma propriedade (uso interno, não enviar ao produtor):
o que pedir ao responsável, o que já chegou, a conferência das imagens e do cadastro, e uma
mensagem pronta para mandar por WhatsApp ou e-mail.

Uso (na raiz do repositório):
    uv run ferramentas/gerar_controle.py sanga-dos-touros   → Recorrida app/Propriedades/<pasta>/Controle-implantacao-<pasta>.docx
    uv run ferramentas/gerar_controle.py --modelo           → Recorrida app/Implantacao/Controle-implantacao-MODELO.docx

O documento é gerado UMA vez, no início, e depois você o preenche à mão no Word (datas, ☐ → ☒,
anotações). Por isso a ferramenta não sobrescreve um Controle que já existe (use --refazer para gerar
de novo, perdendo o que foi escrito). As anotações ficam só no OneDrive: o repositório é público.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from docx_comum import APP, CINZA, RAIZ, caixa, checklist, lista, novo_documento, par, salvar, tabela  # noqa: E402

ITENS = [
    ("Planilha de cadastro (.xlsx)",
     "Enviar o arquivo Cadastro-propriedade-Recorrida.xlsx e pedir que preencham:\n"
     "• Usuários: nome e e-mail Google de cada pessoa, e o acesso de cada uma: **Só o app**, **App e planilha (editor)** ou **(só visualização)**;\n"
     "• Potreiros: todos, com o nome usado no campo e os apelidos;\n"
     "• Minerais: produtos do cocho e kg por saco;\n"
     "• Categorias: conferir a sugestão e numerar na **ordem em que devem aparecer no app**;\n"
     "• Medicamentos: produto, tipo e unidade da dose;\n"
     "• Aba Propriedade: nome, responsável, movimentação opcional (SIM/NÃO)."),
    ("Marca / logo",
     "O arquivo original, o maior que tiverem (de preferência PNG com fundo transparente, SVG ou PDF da gráfica). "
     "Se só houver foto ou print, serve: será redesenhado (vetorizado)."),
    ("Foto de referência",
     "Uma foto **horizontal** da propriedade ou da lida no campo, original (não print, não reenviada pelo WhatsApp, "
     "que reduz a qualidade). Vai no topo do app. Perguntar quem é o autor e se pode ser usada."),
]


def gerar(d: dict, destino: Path, modelo=False):
    nome = d["nomeCompleto"]
    ctl = {}
    doc = novo_documento(f"Controle · {nome}")
    doc.add_paragraph(f"Controle da implantação: {nome}", style="Title")
    par(doc, "Uso interno: o que pedir ao responsável e o que já chegou. Não enviar ao produtor "
             "(para os usuários, o documento é o de Boas-vindas).", cor=CINZA)

    doc.add_heading("1. Dados", level=1)
    tabela(doc, ["Campo", "Valor"], [
        ["Propriedade", nome],
        ["Responsável", ctl.get("responsavel", "")],
        ["Telefone / e-mail", ctl.get("contato", "")],
        ["Pasta de registro", "Recorrida app/Propriedades/" + (d.get("pastaRegistro") or "{{PASTA}}") + "/"],
        ["Endereço do app", d.get("endereco", "")],
        ["Planilha Google", d.get("planilhaUrl") or "(a criar)"],
    ], [4.6, 12.0])

    doc.add_heading("2. O que pedir", level=1)
    tabela(doc, ["Item", "O que pedir", "Pedido em", "Recebido em", "Conferido"],
           [[i, t, "", "", "☐"] for i, t in ITENS], [3.0, 8.2, 1.7, 1.8, 1.9])

    doc.add_heading("Mensagem pronta (WhatsApp ou e-mail)", level=2)
    caixa(doc,
          f"Olá! Para montar o aplicativo **Recorrida** da {nome if not modelo else '{{PROPRIEDADE}}'}, preciso de três coisas:\n"
          "1) A planilha em anexo preenchida: quem vai usar o app (nome e e-mail Google, e se a pessoa usa só o app ou "
          "também a planilha com os dados), os potreiros, os minerais, as categorias na ordem em que querem ver no app "
          "e os medicamentos. Basta escrever nas células amarelas.\n"
          "2) A marca da fazenda, no melhor arquivo que tiverem (o original, não print).\n"
          "3) Uma foto horizontal da fazenda ou do trabalho no campo, para o topo do app. Se a foto for de um "
          "fotógrafo, me digam o nome para eu confirmar que pode ser usada.\n"
          "Qualquer dúvida, é só chamar. Obrigado!", "EEF3F8")

    doc.add_heading("3. Conferir as imagens (sempre)", level=1)
    par(doc, "Salvar o que chegar em **Propriedades/<Nome>/marca/** sem apagar o original. Antes de gerar o app:")
    checklist(doc, [
        "**Logo nítido?** Foto, print, JPEG pequeno ou com fundo branco → vetorizar só o símbolo e salvar como "
        "logo.svg e logo-branco.svg (o nome da fazenda já aparece escrito no app).",
        "**Ícone:** abrir img/icon-192.png depois de gerar: o símbolo precisa ficar legível e sem quadrado branco.",
        "**Foto de referência:** horizontal, com pelo menos 1600 px de largura se possível; salvar uma cópia como foto-topo.jpg.",
        "**Enquadramento:** o topo do app é largo e baixo. Se cortar o rosto ou o assunto, ajustar \"posicaoFotoTopo\" "
        "no propriedade.json (ex.: \"58% 8%\" = horizontal, vertical) e gerar de novo.",
        "**Direitos:** marca d'água ou assinatura de fotógrafo → confirmar autorização (não recortar a assinatura sem permissão). "
        "Pessoa reconhecível na foto → confirmar que ela concorda.",
        "**Tela de entrada:** é igual em todas as propriedades (Recorrida, foto do Juca e a homenagem). Não precisa pedir foto para ela.",
    ])

    doc.add_heading("4. Conferir o cadastro", level=1)
    checklist(doc, [
        "E-mails completos, sem espaços; cada pessoa com **Acesso** marcado (Só o app / App e planilha editor / só visualização). Editor também libera pessoas no app: só para quem responde pela propriedade.",
        "Potreiros sem nomes repetidos; apelidos separados por ponto e vírgula.",
        "Categorias numeradas na ordem do app, com a espécie certa.",
        "Minerais com kg por saco; medicamentos com tipo e unidade.",
        "Movimentação opcional respondida (na dúvida, SIM para equipes com pouca prática no celular).",
        "Pendências → voltar ao responsável e anotar abaixo.",
    ])

    doc.add_heading("5. Andamento", level=1)
    par(doc, "Passo a passo detalhado no Roteiro de implantação (item 4).", cor=CINZA)
    checklist(doc, [
        "Fase A · Coleta: cadastro, marca e foto recebidos e conferidos.",
        "Fase B · Planilha e servidor criados; cadastro importado; /exec anotado.",
        "Fase C · App gerado (gerar.py) e publicado (Push).",
        "Fase D · Teste feito; planilha compartilhada (o importarCadastro faz e mostra no registro); Boas-vindas enviado.",
        "Primeira semana acompanhada.",
    ])

    doc.add_heading("6. Anotações", level=1)
    notas = ctl.get("notas", [])
    if notas:
        lista(doc, notas)
    for _ in range(3 if notas else 6):
        par(doc, "_" * 95, cor=CINZA)
    salvar(doc, destino)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--modelo":
        gerar({"nomeCompleto": "{{PROPRIEDADE}}"}, APP / "Implantacao/Controle-implantacao-MODELO.docx", modelo=True)
    else:
        refazer = "--refazer" in a
        for slug in [x for x in a if x != "--refazer"]:
            d = json.loads((RAIZ / "propriedades" / slug / "propriedade.json").read_text(encoding="utf-8"))
            pasta = d.get("pastaRegistro") or d["nomeCurto"]
            destino = APP / "Propriedades" / pasta / f"Controle-implantacao-{pasta.replace(' ', '-')}.docx"
            if destino.exists() and not refazer:
                print("Já existe (não sobrescrevi; edite no Word ou use --refazer):", destino)
                continue
            gerar(d, destino)
