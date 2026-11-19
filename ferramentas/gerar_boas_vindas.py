# /// script
# dependencies = ["python-docx", "qrcode[pil]"]
# ///
"""
Recorrida — documento de BOAS-VINDAS para os usuários da propriedade (enviado na entrega).

Uso (na raiz do repositório):
    uv run ferramentas/gerar_boas_vindas.py sanga-dos-touros  → Recorrida app/Propriedades/<pasta>/Boas-vindas-Recorrida-<pasta>.docx
    uv run ferramentas/gerar_boas_vindas.py --modelo          → Recorrida app/Implantacao/Boas-vindas-Recorrida-MODELO.docx

Lê de propriedades/<slug>/propriedade.json: nomeCompleto, endereco (link do app), planilhaUrl,
nomeIcone, pastaRegistro. O contato de suporte vem de ferramentas/suporte.json.
O que VOCÊ pede ao responsável fica em outro documento: gerar_controle.py.
"""
import io
import json
import sys
from datetime import date
from pathlib import Path

import qrcode
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

sys.path.insert(0, str(Path(__file__).parent))
from docx_comum import APP, CINZA, MARROM, RAIZ, caixa, lista, link, novo_documento, par, salvar, tabela  # noqa: E402


def gerar(d: dict, destino: Path, modelo=False):
    nome = d["nomeCompleto"]
    doc = novo_documento(f"Recorrida · {nome}")
    doc.add_paragraph("Bem-vindo ao Recorrida!", style="Title")
    par(doc, f"**{nome}**", cor=MARROM, tam=13)
    par(doc, ("Entregue em " + date.today().strftime("%d/%m/%Y")) if not modelo else "Entregue em {{DATA}}", cor=CINZA, tam=9)

    par(doc, "**Parabéns por adquirir o app Recorrida!** A partir de agora, a recorrida do campo fica registrada no "
             "celular: a lotação de cada potreiro, o mineral colocado no cocho, os medicamentos aplicados e a "
             "movimentação dos animais (nascimentos, mortes, vendas, transferências).")
    par(doc, "Tudo funciona **mesmo sem sinal de internet**. Os registros ficam guardados no celular e seguem sozinhos "
             "para a planilha da propriedade assim que houver conexão. Este guia mostra como instalar e começar a usar.")

    doc.add_heading("1. Abra o app", level=1)
    p = par(doc, "**Link do app:** ")
    if modelo:
        p.add_run("{{LINK_APP}}")
    else:
        link(p, d["endereco"])
    if modelo:
        par(doc, "{{QR_CODE do link do app}}", italico=True, cor=CINZA)
    else:
        img = qrcode.make(d["endereco"], box_size=10, border=2)
        buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(buf, width=Cm(4.2))
        p = par(doc, "Aponte a câmera do celular para o código e toque no link que aparecer", cor=CINZA, tam=9)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("2. Instale no celular", level=1)
    par(doc, "O Recorrida não fica na App Store nem no Google Play: ele é instalado direto pelo navegador, "
             "em menos de um minuto. Depois disso, abre como qualquer outro aplicativo, pelo ícone na tela.")
    icone = "{{NOME_ICONE}}" if modelo else d.get("nomeIcone", "Recorrida")
    doc.add_heading("iPhone", level=2)
    lista(doc, [
        "Abra o link do app no **Safari** (precisa ser o Safari) ou aponte a câmera para o QR code.",
        "**Antes de instalar, libere a localização de vez:** toque no botão **aA** (ou no ícone de ajustes, à esquerda do "
        "endereço) → **Ajustes do Site** → **Localização** → **Permitir**. Assim o iPhone não pergunta mais.",
        "Toque no botão **Compartilhar** (quadrado com uma seta para cima, na barra de baixo ou de cima).",
        "Role e toque em **Adicionar à Tela de Início**. Se não aparecer, toque em \"Editar ações\" e ative essa opção.",
        f"Confira o nome (**{icone}**) e toque em **Adicionar**.",
        "Abra o app pelo novo ícone na tela de início (não pelo Safari).",
    ], numerada=True)
    doc.add_heading("Android", level=2)
    lista(doc, [
        "Abra o link do app no **Chrome** ou aponte a câmera para o QR code.",
        "Quando o Chrome perguntar sobre a localização, toque em **Permitir** (ou \"Durante o uso do app\").",
        "Se aparecer o aviso **Instalar app**, toque nele. Se não aparecer, toque nos **três pontinhos ⋮** (canto de cima).",
        "Toque em **Instalar app** ou **Adicionar à tela inicial** e confirme em **Instalar**.",
        f"Abra o app pelo novo ícone (**{icone}**).",
    ], numerada=True)

    doc.add_heading("Localização: deixe sempre liberada", level=2)
    par(doc, "O app usa a localização do celular para mostrar **os potreiros mais próximos** de onde você está. "
             "Se aparecer \"Localização não liberada\", siga os passos do seu celular:")
    tabela(doc, ["Celular", "Como liberar de vez"], [
        ["**iPhone**",
         "1) **Ajustes → Privacidade e Segurança → Serviços de Localização**: ativado; e, na mesma tela, **Sites do Safari** → "
         "\"Durante o Uso\", com **Localização Precisa** ligada.\n"
         "2) No Safari, no endereço do app: **aA → Ajustes do Site → Localização → Permitir** (o ideal é fazer antes de "
         "adicionar à Tela de Início).\n"
         "3) Se o app instalado ainda perguntar: **Ajustes → Safari** (no iOS 18: Ajustes → Apps → Safari) → "
         "**Localização → Permitir**."],
        ["**Android**",
         "1) **Configurações → Localização**: ativada.\n"
         "2) **Configurações → Apps → Chrome → Permissões → Local** → \"Permitir apenas durante o uso do app\", com "
         "**Usar local exato** ligado.\n"
         "3) Se você tocou em \"Bloquear\" sem querer: no Chrome, abra o link do app, toque no ícone à esquerda do endereço → "
         "**Permissões → Localização** → ativar (ou ⋮ → Configurações → Configurações do site → Localização)."],
    ], [2.6, 14.0])

    doc.add_heading("3. Primeiro acesso", level=1)
    lista(doc, [
        "Toque em **Fazer login com o Google** e escolha o seu e-mail (o mesmo que foi informado no cadastro).",
        "O login é pedido **uma vez só** em cada celular. Depois, o app abre direto, com ou sem internet.",
        "Se aparecer \"e-mail não autorizado\", fale com o responsável pelo app na propriedade: ele libera o seu e-mail.",
    ])

    doc.add_heading("4. No dia a dia", level=1)
    lista(doc, [
        "**Registro:** escolha o potreiro, confira os animais, marque o mineral e os medicamentos, e salve.",
        "**Lotação e Painel:** mostram quantos animais há em cada potreiro e o resumo do período.",
        "**Sem sinal, sem problema.** O selo no topo mostra se está tudo **Sincronizado** ou quantos registros estão "
        "pendentes. O botão **Sincronizar** envia na hora, quando houver internet.",
        "**Antes de trocar de celular, apagar o app ou limpar os dados do navegador**, confira se está \"Sincronizado\": "
        "o que não foi enviado fica só naquele aparelho.",
        "As atualizações do app chegam sozinhas. Se algo novo não aparecer, feche o app e abra de novo com internet.",
    ])

    doc.add_heading("5. Para quem tem acesso à planilha", level=1)
    p = par(doc, "Quem foi cadastrado com acesso **\"App e planilha\"** também vê todos os registros na planilha Google: ")
    if modelo:
        p.add_run("{{LINK_PLANILHA}}")
    elif d.get("planilhaUrl"):
        link(p, d["planilhaUrl"], "abrir a planilha")
    else:
        p.add_run("(link enviado junto com este guia)")
    tabela(doc, ["Para...", "Faça na planilha"], [
        ["Liberar uma pessoa nova", "Aba **Usuarios**: nova linha com o e-mail Google, o nome e Ativo = SIM."],
        ["Bloquear uma pessoa", "Aba **Usuarios**: Ativo = NÃO (vale para todos os celulares dela)."],
        ["Bloquear um celular perdido", "Aba **Aparelhos**: Ativo = NÃO na linha do aparelho."],
        ["Novo potreiro, mineral, categoria ou medicamento",
         "Abas **Potreiros**, **Minerais**, **Categorias** ou **Medicamentos**: acrescente uma linha. "
         "Para tirar da lista do app, Ativo = NÃO (não apague a linha). As categorias aparecem no app na ordem da aba."],
        ["Mudar a forma de registrar a movimentação",
         "Aba **Configuração**, linha \"Movimentação opcional\": SIM ou NÃO. Vale nos celulares depois da próxima sincronização."],
        ["Ver o resumo", "Aba **Painel**: troque o período na célula B4, ou use o menu Recorrida > Atualizar painel."],
    ], [5.2, 11.4])
    caixa(doc, "**Cuidado:** não apague nem mude a ordem das colunas da aba **Recorridas**. Para corrigir um registro, "
               "o melhor é editar pelo próprio app (aba Registros), que mantém a planilha e os celulares iguais.")

    doc.add_heading("6. Precisa de ajuda?", level=1)
    sup = json.loads((Path(__file__).parent / "suporte.json").read_text(encoding="utf-8"))
    par(doc, "Dúvidas, sugestões ou problemas: **" + sup.get("nome", "") + "**" +
        ((" · " + sup["contato"]) if sup.get("contato") else "  ·  {{CONTATO}}"))
    par(doc, "Bom trabalho e boas recorridas!", italico=True, cor=MARROM)
    salvar(doc, destino)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--modelo":
        gerar({"nomeCompleto": "{{PROPRIEDADE}}"}, APP / "Implantacao/Boas-vindas-Recorrida-MODELO.docx", modelo=True)
    else:
        for slug in a:
            d = json.loads((RAIZ / "propriedades" / slug / "propriedade.json").read_text(encoding="utf-8"))
            pasta = d.get("pastaRegistro") or d["nomeCurto"]
            gerar(d, APP / "Propriedades" / pasta / f"Boas-vindas-Recorrida-{pasta.replace(' ', '-')}.docx")
