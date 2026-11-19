#!/usr/bin/env python3
"""Desenha o fluxograma de implantação da Recorrida (PNG) com Pillow.

Uso: python3 ferramentas/fluxograma.py [saida.png]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PADRAO = (Path.home() / "Library/CloudStorage/OneDrive-Pessoal/GPTs e bots/Aplicativos/Recorrida app"
          / "Implantacao/Fluxograma-implantacao-Recorrida.png")
FONTES = "/System/Library/Fonts/Supplemental/"
f = lambda n, s: ImageFont.truetype(FONTES + n, s)
F_TXT, F_NEG, F_TIT, F_PEQ = f("Arial.ttf", 25), f("Arial Bold.ttf", 25), f("Arial Bold.ttf", 34), f("Arial.ttf", 21)

COR = {  # quem faz cada etapa
    "voce": ("#F3E7DC", "#8C4A22", "Você"),
    "produtor": ("#E3EFE0", "#3D6B3F", "Produtor / responsável"),
    "google": ("#E2ECF7", "#2F5D8A", "Você, no Google (planilha e Apps Script)"),
    "github": ("#ECE6F4", "#5B4A8A", "Você, no computador (repositório e GitHub Desktop)"),
}
ETAPAS = [  # (quem, título, detalhe)
    ("voce", "1. Primeiro contato", "Apresentar o app e combinar a movimentação (obrigatória ou opcional).\nEnviar o cadastro .xlsx e pedir a marca e uma foto (mensagem pronta no Controle)."),
    ("produtor", "2. Preencher e devolver", "Usuários (Gmail; só app ou app e planilha), potreiros, minerais,\ncategorias na ordem do app, medicamentos. Marca e foto em separado."),
    ("voce", "3. Conferir o cadastro", "E-mails completos? Nomes de potreiros como a equipe fala?\nKg por saco? Faltou algo → volta ao produtor."),
    ("voce", "4. Registrar a propriedade", "Propriedades/<Nome>/: cadastro e Controle. Imagens em marca/:\nconferir sempre (vetorizar logo, enquadrar foto, direitos de uso)."),
    ("google", "5. Planilha e servidor", "Planilha nova \"<Nome> Recorrida\" → Apps Script: Ponte.gs + biblioteca RecorridaNucleo.\nconfigurar → importarCadastro → conferir as abas e a aba Configuração."),
    ("google", "6. Publicar o servidor", "Implantar → App da Web (executar como eu; qualquer pessoa).\nCopiar a URL /exec."),
    ("github", "7. Gerar o app", "propriedades/<slug>/propriedade.json (nome, cores, URL /exec).\npython3 ferramentas/gerar.py <slug> → commit → Push origin."),
    ("voce", "8. Testar", "Abrir o link, entrar com um Gmail da lista, fazer uma recorrida de teste,\nsincronizar, conferir na planilha e excluir o teste."),
    ("google", "9. Compartilhar a planilha", "Automático no importarCadastro: editor ou só visualização,\nconforme o cadastro. Conferir no registro de execução."),
    ("voce", "10. Boas-vindas", "uv run ferramentas/gerar_boas_vindas.py <slug> → enviar o .docx aos usuários\n(parabéns, link do app e da planilha, como instalar no iPhone e Android)."),
    ("produtor", "11. Instalar e usar", "Cada pessoa instala no celular e entra uma vez com o Gmail."),
    ("voce", "12. Acompanhar a 1ª semana", "Conferir os registros. Se a equipe tiver dificuldade, mudar\n\"Movimentação opcional\" na aba Configuração (sem republicar)."),
]

L, MARG, CX_W, CX_H, ESP = 1500, 60, 1080, 128, 46


def main(saida: Path):
    alt = 200 + len(ETAPAS) * (CX_H + ESP) + 60
    im = Image.new("RGB", (L, alt), "white")
    d = ImageDraw.Draw(im)
    d.text((MARG, 40), "Recorrida — implantação em uma nova propriedade", font=F_TIT, fill="#4A2814")
    # legenda
    x = MARG
    for fundo, borda, nome in COR.values():
        d.rounded_rectangle((x, 100, x + 26, 126), 6, fill=fundo, outline=borda, width=3)
        d.text((x + 36, 101), nome, font=F_PEQ, fill="#333333")
        x += 46 + d.textlength(nome, font=F_PEQ) + 20
    x0 = (L - CX_W) // 2 + 60
    y = 170
    centros = []
    for quem, tit, det in ETAPAS:
        fundo, borda, _ = COR[quem]
        d.rounded_rectangle((x0, y, x0 + CX_W, y + CX_H), 18, fill=fundo, outline=borda, width=3)
        d.text((x0 + 24, y + 14), tit, font=F_NEG, fill=borda)
        for i, linha in enumerate(det.split("\n")):
            d.text((x0 + 24, y + 52 + i * 31), linha, font=F_TXT, fill="#222222")
        centros.append((x0, y))
        y += CX_H + ESP
    # setas
    for (xa, ya), (xb, yb) in zip(centros, centros[1:]):
        cx = xa + CX_W // 2
        d.line((cx, ya + CX_H, cx, yb - 6), fill="#666666", width=4)
        d.polygon([(cx - 11, yb - 18), (cx + 11, yb - 18), (cx, yb - 2)], fill="#666666")
    # volta: 3 → 2 (pendências)
    (x2, y2), (x3, y3) = centros[1], centros[2]
    xl = x0 - 70
    d.line((x0, y3 + CX_H // 2, xl, y3 + CX_H // 2), fill="#B00020", width=4)
    d.line((xl, y3 + CX_H // 2, xl, y2 + CX_H // 2), fill="#B00020", width=4)
    d.line((xl, y2 + CX_H // 2, x0 - 6, y2 + CX_H // 2), fill="#B00020", width=4)
    d.polygon([(x0 - 18, y2 + CX_H // 2 - 11), (x0 - 18, y2 + CX_H // 2 + 11), (x0 - 2, y2 + CX_H // 2)], fill="#B00020")
    txt = "pendências"
    w = d.textlength(txt, font=F_PEQ)
    lbl = Image.new("RGBA", (int(w) + 8, 28), (255, 255, 255, 0))
    ImageDraw.Draw(lbl).text((4, 2), txt, font=F_PEQ, fill="#B00020")
    lbl = lbl.rotate(90, expand=True)
    im.paste(lbl, (xl - 34, (y2 + y3 + CX_H) // 2 - lbl.height // 2), lbl)
    saida.parent.mkdir(parents=True, exist_ok=True)
    im.save(saida, optimize=True)
    print("Gerado:", saida)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else PADRAO)
