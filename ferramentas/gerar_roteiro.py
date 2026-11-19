# /// script
# dependencies = ["python-docx"]
# ///
"""
Recorrida — Roteiro de implantação (para o Rogério).

Uso: uv run ferramentas/gerar_roteiro.py
Saída: Recorrida app/Implantacao/Roteiro-implantacao-Recorrida.docx (usa o PNG do fluxograma).
"""
import sys
from pathlib import Path

from docx.enum.text import WD_BREAK
from docx.shared import Cm

sys.path.insert(0, str(Path(__file__).parent))
from docx_comum import APP, CINZA, caixa, checklist, lista, novo_documento, par, salvar, tabela  # noqa: E402

IMPL = APP / "Implantacao"


def main():
    doc = novo_documento("Roteiro de implantação da Recorrida")
    doc.add_paragraph("Recorrida: roteiro de implantação em novas propriedades", style="Title")
    par(doc, "Uso interno. Modelo híbrido: um único código do app e do servidor, e, para cada propriedade, "
             "endereço, marca, planilha e servidor próprios.", cor=CINZA)

    # ------------------------------------------------------------------ 1
    doc.add_heading("1. Como está organizado", level=1)
    tabela(doc, ["O quê", "Onde"], [
        ["Código do app (igual para todas)", "Repositório **recorrida** → pasta **nucleo/** (~/Documents/GitHub/recorrida)"],
        ["Dados de cada propriedade (nome, cores, URL do servidor, catálogo)", "recorrida/**propriedades/<slug>/** (propriedade.json, catalogo.json, img/)"],
        ["App publicado de cada propriedade", "recorrida/**<slug>/** → https://rferreirasul-arch.github.io/recorrida/<slug>/ "
                                              "(a Santa Rita **não** usa este modelo: continua como está, em …/santa-rita-recorrida/)"],
        ["Servidor (igual para todas)", "Biblioteca Apps Script **Recorrida Núcleo** (arquivos em recorrida/apps-script/: Code, Painel, Dropbox, Cadastro)"],
        ["Servidor de cada propriedade", "Planilha \"<Nome> Recorrida\" → Apps Script com **só o Ponte.gs**, que chama a biblioteca"],
        ["O que muda sem republicar", "Aba **Configuração** da planilha (nome, movimentação opcional, pasta do Dropbox)"],
        ["Documentos e registros", "OneDrive: **Aplicativos/Recorrida app/** (Implantacao, Propriedades/<Nome>, Referencias, Historico)"],
        ["Logo e fotos de cada propriedade", "Recorrida app/Propriedades/<Nome>/**marca/** (regras no LEIA-ME.txt da pasta)"],
    ], [5.6, 11.0])
    caixa(doc, "**Ferramentas** (rodar no Terminal, dentro de ~/Documents/GitHub/recorrida):\n"
               "python3 ferramentas/gerar.py <slug>   ·   gera o app da propriedade (ou --todas)\n"
               "python3 ferramentas/gerar_cadastro.py   ·   refaz a planilha de cadastro em branco\n"
               "uv run ferramentas/gerar_controle.py <slug>   ·   Controle: o que pedir e o que chegou (para você)\n"
               "uv run ferramentas/gerar_boas_vindas.py <slug>   ·   Boas-vindas com QR code (para os usuários)\n"
               "uv run ferramentas/gerar_roteiro.py   ·   este roteiro", "EEF3F8")

    # ------------------------------------------------------------------ 2
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("2. Fluxograma", level=1)
    fluxo = IMPL / "Fluxograma-implantacao-Recorrida.png"
    if fluxo.exists():
        doc.add_picture(str(fluxo), height=Cm(22.5))
    doc.paragraphs[-1].runs[-1].add_break(WD_BREAK.PAGE)

    # ------------------------------------------------------------------ 3
    doc.add_heading("3. O que pedir ao produtor", level=1)
    par(doc, "Gere o **Controle** da propriedade (uv run ferramentas/gerar_controle.py <slug>): ele traz a lista abaixo, "
             "uma mensagem pronta para WhatsApp ou e-mail e onde anotar o que já chegou. "
             "Envie o arquivo **Cadastro-propriedade-Recorrida.xlsx** (pasta Implantacao) e peça:")
    lista(doc, [
        "**Usuários:** nome e **e-mail Google** de cada pessoa, e o acesso de cada uma: **Só o app** ou **App e planilha**.",
        "**Potreiros:** todos, com o nome que a equipe usa no campo e apelidos (nomes alternativos).",
        "**Categorias:** conferir a lista sugerida e numerar na **ordem em que devem aparecer no app**.",
        "**Minerais:** produtos do cocho e kg por saco.",
        "**Medicamentos:** produto, tipo (vermífugo, carrapaticida...) e unidade da dose.",
        "**Movimentação opcional (SIM/NÃO):** NÃO = o app já abre o quadro \"O que aconteceu?\" quando a contagem muda; "
        "SIM = só abre se a pessoa ligar \"Registrar o que mudou\". Para equipes com pouca prática, começar com SIM.",
        "**Imagens (opcional):** a marca (arquivo original; se só houver foto, será vetorizada) e uma foto horizontal "
        "de referência para o topo do app, com o nome do autor. Sem imagens, ficam as padrão. A tela de entrada é igual "
        "para todas (Recorrida, foto do Juca e a homenagem).",
        "**Dropbox (opcional):** se querem a cópia diária em Excel e em qual pasta.",
    ])

    # ------------------------------------------------------------------ 4
    doc.add_heading("4. Passo a passo (cada propriedade)", level=1)
    par(doc, "Exemplo usado abaixo: **Sanga dos Touros**, slug **sanga-dos-touros** "
             "(slug = nome sem acentos, minúsculo, com hífens; vira o endereço do app).", cor=CINZA)

    doc.add_heading("Fase A · Coleta", level=2)
    checklist(doc, [
        "Enviar o cadastro .xlsx e a lista do item 3.",
        "Receber o cadastro preenchido e salvar em Recorrida app/Propriedades/<Nome>/.",
        "Conferir: e-mails completos (sem espaço), nomes de potreiros sem repetição, kg por saco, tipo dos medicamentos. "
        "Pendências → voltar ao produtor.",
        "Salvar as imagens em Propriedades/<Nome>/marca/ (sem apagar os originais) com os nomes: logo.svg ou logo.png, "
        "logo-branco (opcional), icone.png (opcional), foto-topo.jpg.",
        "**Conferir sempre as imagens** (Controle, item 3): vetorizar logo de baixa qualidade, conferir o ícone, "
        "ajustar o enquadramento da foto (posicaoFotoTopo) e confirmar os direitos de uso.",
    ])

    doc.add_heading("Fase B · Planilha e servidor (Google, conta rferreira.sul)", level=2)
    checklist(doc, [
        "Google Drive → nova planilha **\"<Nome> Recorrida\"** (ex.: \"Sanga dos Touros Recorrida\").",
        "Extensões → Apps Script. Renomear o projeto para o mesmo nome. Apagar o conteúdo do Código.gs e colar o **Ponte.gs**.",
        "Bibliotecas (+) → colar o **ID do script da Recorrida Núcleo** → Pesquisar → versão mais recente → identificador **RecorridaNucleo** → Adicionar.",
        "Configurações do projeto (engrenagem) → fuso horário **(GMT-03:00) São Paulo**.",
        "Selecionar a função **configurar** → Executar → autorizar com a sua conta. Cria todas as abas e põe você na aba Usuarios.",
        "Subir o .xlsx do cadastro ao Google Drive → abrir → **Arquivo → Salvar como Planilhas Google** → copiar o link.",
        "No Ponte.gs, colar o link em **CADASTRO_URL** → salvar → executar **importarCadastro**. Ver o resultado no Registro de execução.",
        "Conferir as abas Usuarios, Potreiros, Categorias, Minerais, Medicamentos e **Configuração** "
        "(Propriedade e Movimentação opcional já vêm do cadastro).",
        "Se tiver Dropbox: preencher \"Pasta Dropbox\" na Configuração, colocar DROPBOX_APP_KEY e DROPBOX_APP_SECRET nas "
        "Propriedades do script, rodar dropboxConectar (2 vezes, ver o LEIA-ME), exportarParaDropbox e agendarExportacao.",
        "**Implantar → Nova implantação → App da Web**: executar como **Eu**; quem pode acessar: **Qualquer pessoa**. Copiar a URL /exec.",
        "Abrir a URL /exec no navegador: deve aparecer \"Recorrida (<Nome>): servidor ativo.\"",
    ])

    doc.add_heading("Fase C · App (computador)", level=2)
    checklist(doc, [
        "Em ~/Documents/GitHub/recorrida/propriedades/, copiar a pasta de uma propriedade como modelo para **<slug>/**.",
        "Editar **propriedade.json**: slug, nomeCompleto, nomeCurto, nomeIcone (até 12 letras), cores, **apiUrl** (/exec), "
        "planilhaUrl, banco (\"recorrida-<slug>\"), prefixo (\"rec-<slug>\"), pastaRegistro (nome da pasta no OneDrive), "
        "saida (\"<slug>\"), endereco (https://rferreirasul-arch.github.io/recorrida/<slug>/), movOpcional.",
        "catalogo.json: pode ficar vazio ({}); a lista vem da planilha na primeira sincronização.",
        "Terminal: **python3 ferramentas/gerar.py <slug>**. A ferramenta lista quais imagens vieram da Santa Rita.",
        "GitHub Desktop: repositório recorrida → commit \"Nova propriedade: <Nome>\" → **Push origin**. Em 1 a 2 minutos o endereço fica no ar.",
    ])

    doc.add_heading("Fase D · Teste e entrega", level=2)
    checklist(doc, [
        "Abrir o endereço no celular, entrar com o seu Gmail (já está na aba Usuarios), conferir nome, logo e foto.",
        "Fazer uma recorrida de teste → Sincronizar → conferir a linha na aba Recorridas → excluir o teste pelo app.",
        "Conferir o Painel (menu Recorrida → Atualizar painel).",
        "Compartilhar a planilha (como Editor) com quem marcou **\"App e planilha\"**: o importarCadastro lista esses e-mails.",
        "Terminal: **uv run ferramentas/gerar_boas_vindas.py <slug>** → enviar aos usuários o .docx gerado em Propriedades/<Nome>/.",
        "Anotar no Recorrida app/LEIA-ME.md: endereço, planilha, /exec, ID do script e a data de entrega.",
        "Na primeira semana: acompanhar os registros; se necessário, trocar \"Movimentação opcional\" na aba Configuração.",
    ])

    # ------------------------------------------------------------------ 5
    doc.add_heading("5. Preparação única (feita uma vez)", level=1)
    doc.add_heading("Biblioteca \"Recorrida Núcleo\"", level=2)
    checklist(doc, [
        "script.google.com → Novo projeto → nome **Recorrida Núcleo**; fuso horário São Paulo nas Configurações do projeto.",
        "Criar os arquivos **Code**, **Painel**, **Dropbox** e **Cadastro** e colar o conteúdo de recorrida/apps-script/ (não colar o Ponte.gs).",
        "Implantar → Nova implantação → tipo **Biblioteca** → descrição \"v1\" → Implantar.",
        "Configurações do projeto → copiar o **ID do script** e anotar no LEIA-ME (é o que se cola em Bibliotecas, em cada planilha).",
    ])
    doc.add_heading("Repositório \"recorrida\" no GitHub", level=2)
    checklist(doc, [
        "GitHub Desktop → Add → Add existing repository → ~/Documents/GitHub/recorrida → **Publish repository** "
        "(público; nome recorrida; desmarcar \"Keep this code private\").",
        "github.com/rferreirasul-arch/recorrida → Settings → Pages → Branch **main** / root → Save.",
    ])
    doc.add_heading("Nome do login do Google", level=2)
    caixa(doc, "Hoje a tela de login do Google mostra **\"Fazenda Santa Rita\"** para todos os apps (é o nome do projeto no "
               "Google Cloud). Para outras propriedades, vale trocar em console.cloud.google.com → Google Auth Platform → "
               "Branding para um nome geral (ex.: \"Recorrida\" ou \"Aplicativos Rogério Ferreira\") e apontar a política "
               "de privacidade para uma página geral. Muda para todos os apps (Nascimentos inclusive).")

    # ------------------------------------------------------------------ 6
    doc.add_heading("6. Atualizar todas as propriedades", level=1)
    doc.add_heading("Mudança no app (tela, funções)", level=2)
    lista(doc, [
        "Editar em recorrida/**nucleo/** (nunca nas pastas das propriedades, que são geradas).",
        "Testar localmente (servidor de pré-visualização \"recorrida\", porta 8771).",
        "**python3 ferramentas/gerar.py --todas** → atualiza todas as propriedades do repositório recorrida "
        "(a Santa Rita está marcada como \"congelada\" e não é tocada).",
        "GitHub Desktop: commit e **Push origin** no repositório recorrida.",
    ], numerada=True)
    doc.add_heading("Mudança no servidor (planilha)", level=2)
    lista(doc, [
        "Colar os arquivos alterados de recorrida/apps-script/ no projeto **Recorrida Núcleo**.",
        "Implantar → Gerenciar implantações → lápis → **Nova versão** → Implantar (anotar o número).",
        "Em cada planilha: Apps Script → Bibliotecas → RecorridaNucleo → escolher a **nova versão** → Salvar. "
        "Não precisa mexer na implantação do App da Web: a URL /exec não muda.",
        "Se a mudança acrescentou chaves na Configuração, rodar configurar uma vez (não apaga nada).",
    ], numerada=True)
    caixa(doc, "Por que versão fixa e não \"mais recente\"? Uma versão com erro na biblioteca não derruba todas as propriedades "
               "de uma vez: dá para atualizar uma propriedade de teste primeiro (Sanga dos Touros) e as outras depois.")

    # ------------------------------------------------------------------ 7
    doc.add_heading("7. Santa Rita: fica como está", level=1)
    caixa(doc, "Decisão de 19/11/2026: o app da **Santa Rita** está em uso e **não muda**. Continua no repositório "
               "santa-rita-recorrida, com o servidor antigo, sem biblioteca e sem a aba Configuração. O modelo novo vale, "
               "em fase de teste, só para a **Sanga dos Touros**. No gerador, a Santa Rita está marcada como \"congelada\": "
               "as imagens dela servem apenas de padrão para as outras propriedades.")
    par(doc, "Se um dia a Santa Rita passar para o modelo novo, o caminho é: cópia de segurança da planilha; Ponte.gs + "
             "biblioteca no Apps Script dela; configurar (cria a aba Configuração; Pasta Dropbox = /Fazenda Santa Rita -2023/Apps "
             "Santa Rita); agendarExportacao; e Implantar → Gerenciar implantações → Nova versão (mantém a URL /exec). "
             "Só depois de bem testado na Sanga dos Touros.", cor=CINZA)

    # ------------------------------------------------------------------ 8
    doc.add_heading("8. Problemas comuns", level=1)
    tabela(doc, ["Sintoma", "Causa e solução"], [
        ["\"O e-mail … não está autorizado\"", "Falta a pessoa na aba Usuarios (ou Ativo = NÃO). Acrescentar e tentar de novo."],
        ["\"Login emitido para outro aplicativo\"", "CLIENT_ID diferente entre o propriedade.json e o Code.gs da biblioteca."],
        ["App não mostra a mudança", "Fechar e abrir o app com internet. Conferir se o Push foi feito e se o Pages terminou de publicar."],
        ["\"Movimentação opcional\" não mudou no celular", "Vale depois da próxima sincronização: tocar em Sincronizar."],
        ["Menu Recorrida não aparece na planilha", "Recarregar a planilha. Conferir se o Ponte.gs tem onOpen e a biblioteca está adicionada."],
        ["importarCadastro: \"e-mail inválido\"", "Corrigir o e-mail na aba Usuários do cadastro e rodar de novo (não duplica o resto)."],
        ["Dados de duas propriedades misturados no mesmo celular", "Não acontece: cada propriedade guarda com nome próprio (campos banco e prefixo do "
                                                                  "propriedade.json). Nunca repetir esses valores entre propriedades."],
    ], [5.6, 11.0])
    salvar(doc, IMPL / "Roteiro-implantacao-Recorrida.docx")


if __name__ == "__main__":
    main()
