#!/usr/bin/env python3
"""
Recorrida — gera o app de uma propriedade a partir do código comum (nucleo/).

Uso (na raiz do repositório):
    python3 ferramentas/gerar.py sanga-dos-touros
    python3 ferramentas/gerar.py --todas

O que faz:
  1. Lê propriedades/<slug>/propriedade.json e catalogo.json.
  2. Lê as imagens da pasta de registro da propriedade
     (OneDrive: "Recorrida app/Propriedades/<pasta>/marca/"), ajusta tamanho e
     peso e guarda em propriedades/<slug>/img/. O que faltar vem da Santa Rita.
  3. Monta a pasta publicada (propriedade.json → "saida"): index.html,
     manifest, privacidade, sw.js e config.js com os dados da propriedade.

Só usa a biblioteca Pillow (já instalada). Não apaga nada fora da pasta img/ da saída.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
NUCLEO = RAIZ / "nucleo"
PROPS = RAIZ / "propriedades"
PADRAO = PROPS / "santa-rita" / "img"  # imagens usadas quando a propriedade não tem as suas
PASTA_REGISTROS = Path(os.environ.get(
    "RECORRIDA_REGISTROS",
    Path.home() / "Library/CloudStorage/OneDrive-Pessoal/GPTs e bots/Aplicativos/Recorrida app/Propriedades",
))

COPIAR = ["app.js", "styles.css"]                         # iguais para todas
MODELOS = ["index.html", "manifest.webmanifest", "privacidade.html", "sw.js"]  # com {{CAMPOS}}
FOTO_MAX = 1600       # px no lado maior
FOTO_KB = 300         # peso máximo aproximado


def aviso(msg):
    print("   ·", msg)


# ---------------------------------------------------------------- imagens
def svg_para_png(svg: Path, lado=1024) -> Image.Image | None:
    """Converte SVG em PNG com o Quick Look do macOS (o fundo branco vira transparente; serve para o ícone)."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(["qlmanage", "-t", "-s", str(lado), "-o", tmp, str(svg)],
                           check=True, capture_output=True, timeout=60)
            png = Path(tmp) / (svg.name + ".png")
            if not png.exists():
                return None
            im = Image.open(png).convert("RGB")
            # o Quick Look põe fundo branco: o quanto o pixel se afasta do branco vira opacidade
            from PIL import ImageChops
            alfa = ImageChops.invert(im.convert("L")).point(lambda v: min(255, v * 3))
            rgba = im.convert("RGBA"); rgba.putalpha(alfa)
            caixa = alfa.getbbox()
            return rgba.crop(caixa) if caixa else rgba
        except Exception:
            return None


def salvar_foto(orig: Path, dest: Path):
    im = ImageOps.exif_transpose(Image.open(orig)).convert("RGB")
    im.thumbnail((FOTO_MAX, FOTO_MAX))
    for q in (85, 78, 70, 62, 55):
        im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)
        if dest.stat().st_size <= FOTO_KB * 1024:
            break


def logo_branco(im: Image.Image) -> Image.Image:
    """Mesma forma do logo, toda em branco (para usar sobre a foto)."""
    im = im.convert("RGBA")
    branco = Image.new("RGBA", im.size, (255, 255, 255, 0))
    branco.putalpha(im.getchannel("A"))
    return branco


def icones(base: Image.Image, cor_fundo: str, dest: Path, margem=0.18):
    """Ícones quadrados 180/192/512 com o logo no centro (margem para o recorte do Android)."""
    base = base.convert("RGBA")
    for lado in (180, 192, 512):
        fundo = Image.new("RGBA", (lado, lado), cor_fundo)
        util = int(lado * (1 - 2 * margem))
        im = base.copy()
        im.thumbnail((util, util), Image.LANCZOS)
        fundo.alpha_composite(im, ((lado - im.width) // 2, (lado - im.height) // 2))
        fundo.convert("RGB").save(dest / f"icon-{lado}.png", optimize=True)


def preparar_imagens(cfg: dict, slug: str) -> dict:
    """Atualiza propriedades/<slug>/img a partir da pasta marca/ e devolve os nomes dos logos."""
    img = PROPS / slug / "img"
    img.mkdir(parents=True, exist_ok=True)
    marca = PASTA_REGISTROS / cfg.get("pastaRegistro", "") / "marca"
    tem = lambda n: (marca / n) if (marca / n).exists() else None
    if not marca.exists():
        aviso(f"pasta de marca não encontrada ({marca}); usando o que já está em propriedades/{slug}/img")

    # Fotos
    for nome_marca, nome_app in (("foto-topo.jpg", "fundo-topo.jpg"), ("foto-entrada.jpg", "fundo-entrada.jpg")):
        orig = tem(nome_marca) or tem(nome_marca.replace(".jpg", ".jpeg")) or tem(nome_marca.replace(".jpg", ".png"))
        if orig:
            salvar_foto(orig, img / nome_app)
            aviso(f"{nome_app}: da propriedade ({orig.name})")

    # Logo
    logo_svg, logo_png = tem("logo.svg"), tem("logo.png")
    logo_img = None
    for velho in ("logo.svg", "logo.png"):  # um logo novo substitui o anterior
        if (logo_svg or logo_png) and (img / velho).exists():
            (img / velho).unlink()
    if logo_svg:
        shutil.copy2(logo_svg, img / "logo.svg")
        aviso("logo.svg: da propriedade")
    elif logo_png:
        logo_img = Image.open(logo_png).convert("RGBA")
        logo_img.thumbnail((800, 800))
        logo_img.save(img / "logo.png", optimize=True)
        aviso("logo.png: da propriedade")

    br_svg, br_png = tem("logo-branco.svg"), tem("logo-branco.png")
    if br_svg or br_png:
        for velho in ("logo-branco.svg", "logo-branco.png"):
            if (img / velho).exists():
                (img / velho).unlink()
    if br_svg:
        shutil.copy2(br_svg, img / "logo-branco.svg"); aviso("logo-branco.svg: da propriedade")
    elif br_png:
        im = Image.open(br_png).convert("RGBA"); im.thumbnail((800, 800))
        im.save(img / "logo-branco.png", optimize=True); aviso("logo-branco.png: da propriedade")
    elif logo_img is not None:
        logo_branco(logo_img).save(img / "logo-branco.png", optimize=True)
        aviso("logo-branco.png: gerado a partir do logo")
    elif logo_svg:
        shutil.copy2(logo_svg, img / "logo-branco.svg")
        aviso("logo-branco: não enviado; usando o próprio logo.svg (envie um logo-branco para ficar melhor sobre a foto)")

    # Ícones
    icone = tem("icone.png") or tem("icone.jpg")
    if icone:
        icones(Image.open(icone), cfg["corFundo"], img, margem=0.0)
        aviso(f"ícones: de {icone.name}")
    elif logo_img is not None or logo_svg:
        base = logo_img if logo_img is not None else svg_para_png(logo_svg)
        if base is not None:
            icones(base, cfg["corFundo"], img)
            aviso("ícones: gerados a partir do logo")
        else:
            aviso("ícones: não foi possível converter o logo.svg; envie um icone.png")

    # O que faltou vem da Santa Rita
    nomes = {}
    for chave, opcoes in (("LOGO", ("logo.svg", "logo.png")), ("LOGO_BRANCO", ("logo-branco.svg", "logo-branco.png"))):
        achado = next((o for o in opcoes if (img / o).exists()), None)
        if not achado:
            achado = opcoes[0]
            shutil.copy2(PADRAO / achado, img / achado)
            aviso(f"{achado}: da Santa Rita (a propriedade não enviou)")
        nomes[chave] = achado
    for n in ("fundo-topo.jpg", "fundo-entrada.jpg", "icon-180.png", "icon-192.png", "icon-512.png"):
        if not (img / n).exists():
            shutil.copy2(PADRAO / n, img / n)
            aviso(f"{n}: da Santa Rita (a propriedade não enviou)")
    return nomes


# ---------------------------------------------------------------- montagem
LEGENDA_PADRAO = "Em homenagem ao Juca, nossa inspiração"
ICONES_SR_V1 = "806256"  # ícones da Santa Rita já publicados com ?v=1 (mantém o endereço)


def _hash_icones(saida: Path) -> str:
    h = hashlib.sha1()
    for n in ("icon-180.png", "icon-192.png", "icon-512.png"):
        h.update((saida / "img" / n).read_bytes())
    return h.hexdigest()[:6]



def gerar(slug: str):
    pasta = PROPS / slug
    cfg = json.loads((pasta / "propriedade.json").read_text(encoding="utf-8"))
    if cfg.get("congelada"):
        print(f"\n■ {cfg['nomeCompleto']}: congelada (\"congelada\": true no propriedade.json), não gerada.")
        return
    catalogo = json.loads((pasta / "catalogo.json").read_text(encoding="utf-8")) if (pasta / "catalogo.json").exists() else {}
    saida = (RAIZ / cfg["saida"]).resolve()
    print(f"\n▶ {cfg['nomeCompleto']}  →  {saida}")

    nomes = preparar_imagens(cfg, slug)

    saida.mkdir(parents=True, exist_ok=True)
    (saida / "img").mkdir(exist_ok=True)
    # Imagens da propriedade + minerais (comuns)
    for f in (pasta / "img").iterdir():
        if f.is_file():
            shutil.copy2(f, saida / "img" / f.name)
    shutil.copytree(NUCLEO / "img" / "minerais", saida / "img" / "minerais", dirs_exist_ok=True)
    # Logos que não são mais usados (ex.: trocou svg por png)
    for velho in ("logo.svg", "logo.png", "logo-branco.svg", "logo-branco.png"):
        if velho not in nomes.values() and (saida / "img" / velho).exists():
            (saida / "img" / velho).unlink()

    for f in COPIAR:
        shutil.copy2(NUCLEO / f, saida / f)

    config = {
        "API_URL": cfg.get("apiUrl", ""),
        "CLIENT_ID": cfg.get("clientId", ""),
        "BANCO": cfg["banco"],
        "PREFIXO": cfg["prefixo"],
        "MOV_OPCIONAL": bool(cfg.get("movOpcional", False)),
        "CATALOGO": catalogo,
    }
    (saida / "config.js").write_text(
        "// Gerado por ferramentas/gerar.py a partir de propriedades/" + slug + "/ — não edite aqui.\n"
        "// Com API_URL vazio, o app roda em MODO DEMONSTRAÇÃO (salva só no aparelho).\n"
        "// MOV_OPCIONAL vale só até a primeira sincronização; depois vale a aba \"Configuração\" da planilha.\n"
        "window.APP_CONFIG = " + json.dumps(config, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8")

    # Versão do cache: muda sempre que algum arquivo muda
    h = hashlib.sha1()
    for f in sorted((saida / "img").rglob("*")) + [saida / x for x in COPIAR + ["config.js"]]:
        if f.is_file():
            h.update(f.read_bytes())
    for m in MODELOS:
        h.update((NUCLEO / m).read_bytes())
    h.update(json.dumps(cfg, sort_keys=True).encode())
    campos = {
        "NOME_APP": cfg.get("nomeApp") or f"{cfg['nomeCurto']} Recorrida",
        "NOME_COMPLETO": cfg["nomeCompleto"],
        "NOME_CURTO": cfg["nomeCurto"],
        "NOME_ICONE": cfg.get("nomeIcone", "Recorrida"),
        "COR_TEMA": cfg["corTema"],
        "COR_FUNDO": cfg["corFundo"],
        "PREFIXO": cfg["prefixo"],
        "VERSAO": "v" + h.hexdigest()[:8],
        # muda só quando os ícones mudam (trocar o endereço do ícone faz o Android atualizar o app instalado)
        "V_IMG": "1" if slug == "santa-rita" and _hash_icones(saida) == ICONES_SR_V1 else _hash_icones(saida),
        # homenagem que acompanha a foto padrão da tela de entrada
        "LEGENDA_ENTRADA": cfg.get("legendaEntrada", LEGENDA_PADRAO if (pasta / "img" / "fundo-entrada.jpg").read_bytes()
                                   == (PADRAO / "fundo-entrada.jpg").read_bytes() else ""),
        # enquadramento da foto do topo ("posicaoFotoTopo": "60% 18%" = horizontal vertical)
        "ESTILO_PROPRIEDADE": (f'  <style>.hero {{ background-position: 0 0, {cfg["posicaoFotoTopo"]}; }}</style>\n'
                               if cfg.get("posicaoFotoTopo") else ""),
        **nomes,
    }
    for m in MODELOS:
        txt = (NUCLEO / m).read_text(encoding="utf-8")
        for k, v in campos.items():
            txt = txt.replace("{{" + k + "}}", v)
        assert "{{" not in txt, f"campo sem valor em {m}: " + txt[txt.index("{{"):txt.index("{{") + 30]
        (saida / m).write_text(txt, encoding="utf-8")
    print(f"   ✓ pronto (cache {campos['VERSAO']})  ·  movimentação opcional no config.js: {'SIM' if config['MOV_OPCIONAL'] else 'NÃO'}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    slugs = sorted(p.name for p in PROPS.iterdir() if (p / "propriedade.json").exists()) if args == ["--todas"] else args
    for s in slugs:
        gerar(s)
