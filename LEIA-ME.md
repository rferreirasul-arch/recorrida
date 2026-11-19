# Recorrida

App para registrar, em cada potreiro, a **lotação** (animais por categoria), o **mineral** colocado no cocho,
medicamentos e a movimentação de animais. Funciona **sem sinal** e envia os registros para uma **planilha Google**
quando a internet volta. **Um código para várias propriedades**: cada propriedade tem endereço, marca, planilha e
servidor próprios.

Documentação de implantação (roteiro, cadastro, controle, boas-vindas, lista de propriedades):
OneDrive › `Aplicativos/Recorrida app/` (comece pelo `LEIA-ME.md` de lá).

```
Celular (app da propriedade)  ──►  Apps Script da planilha  ──►  Planilha "<Nome> Recorrida"
  <slug>/ neste repositório         Ponte.gs → biblioteca          abas Recorridas, Potreiros, ...
  guarda tudo offline (IndexedDB)   "Recorrida Núcleo"             e Configuração
```

## Repositório

| Pasta | Conteúdo |
|---|---|
| `nucleo/` | código do app, **igual para todas** (app.js, styles.css; index.html, manifest, privacidade e sw.js com `{{CAMPOS}}`) |
| `propriedades/<slug>/` | `propriedade.json` (nome, cores, URL do servidor, nomes de armazenamento), `catalogo.json` (listas iniciais), `img/` |
| `<slug>/` | app publicado da propriedade, **gerado** (não editar à mão) |
| `apps-script/` | servidor: `Code.gs`, `Painel.gs`, `Dropbox.gs`, `Cadastro.gs` (biblioteca "Recorrida Núcleo") e `Ponte.gs` (vai em cada planilha) |
| `ferramentas/` | `gerar.py` (monta `<slug>/`), `gerar_cadastro.py`, `fluxograma.py`, `gerar_roteiro.py`, `gerar_controle.py`, `gerar_boas_vindas.py` |

```bash
python3 ferramentas/gerar.py sanga-dos-touros    # uma propriedade
python3 ferramentas/gerar.py --todas             # todas (a Santa Rita está congelada: não é gerada)
```

O `gerar.py` lê as imagens de `Recorrida app/Propriedades/<pastaRegistro>/marca/` (OneDrive). O que faltar vem da
Santa Rita. A versão do cache (`sw.js`) muda sozinha quando algum arquivo muda.

**Campos do `propriedade.json`:** `slug`, `nomeCompleto`, `nomeCurto`, `nomeIcone` (até 12 letras), `corTema`,
`corFundo`, `apiUrl` (/exec; vazio = modo demonstração), `clientId`, `planilhaUrl`, `banco` e `prefixo` (**únicos
por propriedade**: todas ficam no mesmo endereço github.io), `movOpcional` (vale até a primeira sincronização),
`pastaRegistro`, `saida`, `endereco`.

**Movimentação opcional:** aba **Configuração** da planilha, linha "Movimentação opcional".
- NÃO: quando a contagem muda, o app já abre o quadro "O que aconteceu?" (como sempre foi na Santa Rita).
- SIM: aparece o botão "Registrar o que mudou". Desligado, salva só a contagem como lotação.

O servidor manda essa configuração no `sync` e no `ping`, e o app guarda no aparelho.

## Abas do app

| Aba | O que faz |
|---|---|
| **Registro** | Escolhe o potreiro (próximos pelo GPS ou busca por parte do nome, sem acento/maiúscula), marca a localização dos cochos, informa animais e/ou mineral |
| **Lotação** | Animais em cada potreiro pela última recorrida com contagem. Tocar num potreiro abre o registro dele |
| **Registros** | Recorridas lançadas, com filtros, edição, exclusão e CSV |
| **Painel** | Animais hoje, sacos e kg no período, mineral por produto, consumo estimado (g/cab/dia) e dias sem abastecer |

## Planilha

**Recorridas**: uma linha por recorrida. Colunas fixas (Data, Potreiro, Lotação, Total animais, Animais, Sacos, Kg,
Mineral, Observações…) e **uma coluna por categoria** (`Animais: Vacas`) e **por mineral** (`Sacos: Proteico 30 M`),
criadas sozinhas conforme aparecem. Isso facilita tabela dinâmica. Lotação: `Conferida`, `Vazio` ou `Não conferida`
(quando só foi colocado mineral).

**Potreiros**: nome, nomes alternativos (a busca também procura neles), Ativo, dois cochos e o contorno.
- Cocho: texto `lat, lon` (pode colar no Google Maps). O app grava sozinho quando alguém marca o cocho.
- Contorno: formato do KML do Google Earth, `lon,lat lon,lat …` (vários polígonos separados por `|`).
  Com contorno, o app sabe em qual potreiro a pessoa está; sem contorno, usa a distância até os cochos.
- `Ativo = NÃO` tira o potreiro da lista sem apagar o histórico.

**Minerais**: nome, nomes alternativos, **kg por saco** (usado no kg total e no consumo), Ativo.
**Categorias**: espécie, nome, nomes alternativos, Ativo.

**Medicamentos**: nome, nomes alternativos, unidade da dose, Ativo e **Tipo** (Vermífugo, Carrapaticida, Endectocida…;
dá para digitar outro ou mais de um separado por vírgula). O Tipo alimenta a sanidade do Painel.
**Medicações**: montada pelo servidor a partir das recorridas (não editar). Uma linha por medicamento, com as
categorias que receberam, a quantidade de animais, a dose por animal e o **total aplicado** (dose × animais).
**Movimentações**: montada pelo servidor (não editar). Ao conferir os animais, o app compara a contagem com a
lotação anterior e, quando há diferença, pergunta o motivo por categoria: faltando, morte (brinco e causa
opcionais), venda/saída, mudança de categoria, nascimento, entrada, animais de outro potreiro ou contagem
anterior errada (diferença sem motivo também conta assim). A lotação de referência (colunas "Animais: ...")
é a contagem + os faltando − os de outro potreiro. Os faltando aparecem na recorrida seguinte do potreiro
(voltaram, ainda faltam, encontrado morto ou não vão voltar), na aba Lotação (cartão "Com falta") e na
seção "Animais faltando" do Painel.
**Transferência entre potreiros**: no quadro de diferença, "Transferência" (saíram) ou "Vieram (transferência)"
pede o outro potreiro ("Já atualizado no outro potreiro" registra só aqui; em "Vieram" a lista mostra os
potreiros que têm a categoria). Ao salvar, o app mostra como fica a lotação dele (números editáveis) e, se confirmado,
cria uma recorrida só de lotação lá, com a observação "Lotação atualizada pela recorrida de ...". Editar a
recorrida refaz essa atualização; se o outro potreiro já registrou a mesma troca, a opção vem desmarcada; excluir também a desfaz. "Vazio" também abre o quadro, para dizer para onde
foram os animais.
**Medicação sem potreiro**: com Medicamentos ligado e sem potreiro escolhido, ao salvar o app pergunta se lança
só a medicação. Se sim, grava um registro com o potreiro em branco (aparece como "Sem potreiro"): os animais
conferidos ficam só na medicação e não mudam a lotação; mineral, tem mineral e falta no depósito não são salvos.

**Painel**: resumo com tabelas e gráficos (animais por categoria, sacos e consumo de mineral, dias sem abastecer,
mineral em falta, medicamentos e dias após carrapaticida/vermífugo por potreiro). Vem do script `Painel.gs`
(parte da biblioteca). Atualiza ao abrir a planilha, ao trocar o período na célula B4
e pelo menu **Recorrida > Atualizar painel**. A aba é refeita a cada atualização: não digite nada nela.

Potreiros, categorias e minerais novos podem ser incluídos pelo app. Entram na planilha com uma nota
dizendo quem incluiu e quando.
Ao incluir **medicamento**, **categoria** ou **mineral** novos, o app abre uma janela para completar o cadastro:
medicamento pede nomes alternativos, unidade da dose e tipo; categoria pede nomes alternativos e espécie;
mineral pede nomes alternativos e kg por saco.
Unidade, tipo e espécie mostram os já usados na planilha, com a opção de digitar um novo.

## Servidor (Apps Script)

- **Biblioteca "Recorrida Núcleo"**: projeto independente com `Code.gs`, `Painel.gs`, `Dropbox.gs`, `Cadastro.gs`.
  Cada mudança: colar os arquivos, **Implantar → Gerenciar implantações → Nova versão**, e trocar o número da
  versão em **Bibliotecas** no Apps Script de cada planilha.
- **Planilha de cada propriedade**: só o `Ponte.gs`, mais a biblioteca com o identificador `RecorridaNucleo`. A ponte
  entrega à biblioteca as Propriedades, o Cache e o Lock **do script da planilha**, para que as propriedades
  não compartilhem credenciais do Dropbox nem a trava de gravação.
- `configurar`: cria as abas que faltam (inclusive Configuração) sem mexer nas existentes.
- `importarCadastro`: lê a planilha de cadastro (convertida para Google Planilhas, link em `CADASTRO_URL`) e
  acrescenta usuários, potreiros, categorias, minerais e medicamentos sem duplicar. Preenche Propriedade e
  Movimentação opcional na Configuração.
- Também funciona colado direto numa planilha (Code, Painel, Dropbox e Cadastro, sem a ponte), como era antes.

Passo a passo completo: `Recorrida app/Implantacao/Roteiro-implantacao-Recorrida.docx`.

## Cópia diária no Dropbox (só Santa Rita)

As outras propriedades não usam. Na biblioteca o código continua (`Dropbox.gs`), mas só funciona numa planilha que
tenha o `Ponte-Dropbox.gs` e as linhas "Pasta Dropbox"/"Arquivo Dropbox" na aba Configuração.

Todo dia, perto das **5h**, o Apps Script grava o arquivo da linha **Arquivo Dropbox** da aba Configuração
(padrão `Recorrida - consulta.xlsx`) na pasta da linha **Pasta Dropbox** (Santa Rita: `/Fazenda Santa Rita -2023/Apps Santa Rita`),
substituindo a versão anterior. Com a pasta em branco, nada é exportado. A cópia é **só para consulta**:
tem todas as abas, menos Usuarios e Aparelhos, e uma aba **Leia-me** com o link da planilha Google para quem
precisar editar. A pessoa precisa ter acesso de edição à planilha Google.
O código fica em `apps-script/Dropbox.gs` e usa a sua conta do Dropbox, que tem acesso de edição à pasta da fazenda.

Configuração (uma vez só):

1. Aba **Configuração** da planilha: preencher **Pasta Dropbox** (e, se quiser, Arquivo Dropbox).
2. **Dropbox** → <https://www.dropbox.com/developers/apps> → **Create app** → *Scoped access* → *Full Dropbox* →
   nome único (ex.: `Recorrida Exportacao`; o mesmo app do Dropbox pode servir para todas as propriedades).
   - Aba **Permissions**: marcar `files.content.write` → **Submit** (antes do passo 4).
   - Aba **Settings**: anotar **App key** e **App secret**.
3. Apps Script → **Configurações do projeto** (engrenagem) → **Propriedades do script**:
   `DROPBOX_APP_KEY` e `DROPBOX_APP_SECRET`.
4. Executar **`dropboxConectar`**. O registro de execução mostra um link: abrir → **Permitir** → copiar o código →
   criar a propriedade `DROPBOX_CODIGO` com ele → executar `dropboxConectar` de novo ("Dropbox conectado").
5. Executar **`exportarParaDropbox`**. O arquivo deve aparecer na pasta do Dropbox.
6. Executar **`agendarExportacao`**. A partir daí roda sozinho todo dia.

Na primeira execução o Google pede novas autorizações (Drive e agendamento). Se a exportação falhar,
o Google manda e-mail para o dono do script. A hora (5h) fica em `agendarExportacao` no `Ponte.gs`.
