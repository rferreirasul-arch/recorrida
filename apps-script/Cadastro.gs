/**
 * Recorrida — importa a planilha de cadastro preenchida pela propriedade
 * (Implantacao/Cadastro-propriedade-Recorrida.xlsx).
 *
 * Antes: suba o .xlsx recebido para o Google Drive, abra com o Google Planilhas e use
 * Arquivo > Salvar como Planilhas Google. Copie o link dessa cópia para CADASTRO_URL no
 * Ponte.gs e rode importarCadastro. Pode rodar de novo: o que já existe não é duplicado.
 *
 * Modelo das abas do cadastro: linha 1 = título, linha 2 = cabeçalho, linha 3 = exemplo,
 * dados a partir da linha 4.
 */

const CADASTRO_PRIMEIRA_LINHA = 4;

function importarCadastro(url) {
  if (!url) throw new Error("Cole em CADASTRO_URL (Ponte.gs) o link da planilha de cadastro aberta no Google Planilhas.");
  const cad = SpreadsheetApp.openByUrl(url);
  configurar(); // garante as abas e a aba Configuração
  const ss = planilha_();
  const txt = (v) => String(v == null ? "" : v).trim();
  const sim = (v) => (ehNao_(v) ? "NÃO" : "SIM");
  const relatorio = [];

  const linhas = (aba, ncol) => {
    const sh = cad.getSheetByName(aba);
    if (!sh || sh.getLastRow() < CADASTRO_PRIMEIRA_LINHA) return [];
    return sh.getRange(CADASTRO_PRIMEIRA_LINHA, 1, sh.getLastRow() - CADASTRO_PRIMEIRA_LINHA + 1, ncol).getValues()
      .map((l) => l.map(txt)).filter((l) => l.some((c) => c !== ""));
  };
  // Acrescenta no fim da aba as linhas cuja chave (coluna colChave, base 0) ainda não existe
  const acrescentar = (abaDestino, colChave, novas) => {
    const sh = ss.getSheetByName(abaDestino);
    const existentes = {};
    if (sh.getLastRow() > 1) {
      sh.getRange(2, colChave + 1, sh.getLastRow() - 1, 1).getValues().forEach((l) => { existentes[norm_(l[0])] = true; });
    }
    const filtradas = novas.filter((l) => {
      const k = norm_(l[colChave]);
      if (!k || existentes[k]) return false;
      existentes[k] = true;
      return true;
    });
    if (filtradas.length) sh.getRange(sh.getLastRow() + 1, 1, filtradas.length, filtradas[0].length).setValues(filtradas);
    relatorio.push(abaDestino + ": " + filtradas.length + " novo(s)" +
      (novas.length - filtradas.length ? " · " + (novas.length - filtradas.length) + " já existia(m) ou sem nome" : ""));
  };

  // Propriedade (Campo | Resposta) → aba Configuração
  const prop = {};
  const shProp = cad.getSheetByName("Propriedade");
  if (shProp && shProp.getLastRow() >= 3) {
    shProp.getRange(3, 1, shProp.getLastRow() - 2, 2).getValues().forEach((l) => { prop[norm_(l[0])] = txt(l[1]); });
  }
  const achar = (ini) => { const k = Object.keys(prop).find((c) => c.indexOf(norm_(ini)) === 0); return k ? prop[k] : ""; };
  if (achar("Nome completo")) definirConfig_("Propriedade", achar("Nome completo"));
  const mov = achar("Movimentação opcional");
  if (mov) definirConfig_("Movimentação opcional", ehNao_(mov) ? "NÃO" : "SIM");

  // Usuários: Nome | Gmail | Função | Acesso | Ativo  →  Usuarios: E-mail | Nome | Ativo
  // Acesso: "Só o app" · "App e planilha (editor)" · "App e planilha (só visualização)"
  const usuarios = linhas("Usuários", 5);
  const invalidos = usuarios.filter((l) => !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(l[1]));
  if (invalidos.length) relatorio.push("ATENÇÃO, e-mail inválido (não importado): " + invalidos.map((l) => l[0] + " <" + l[1] + ">").join(", "));
  acrescentar(ABA_USUARIOS, 0, usuarios.filter((l) => invalidos.indexOf(l) < 0)
    .map((l) => [l[1].toLowerCase(), l[0], l[4] ? sim(l[4]) : "SIM"]));
  compartilharPlanilha_(ss, usuarios.filter((l) => invalidos.indexOf(l) < 0 && !ehNao_(l[4] || "SIM")), relatorio);

  // Potreiros: Potreiro | Nomes alternativos | Área (ha) | Observações  →  Potreiro | Nomes alternativos | Ativo
  acrescentar(ABA_POTREIROS, 0, linhas("Potreiros", 2).map((l) => [l[0], l[1], "SIM"]));

  // Categorias: Ordem no app | Espécie | Categoria | Nomes alternativos  →  Espécie | Categoria | Nomes alternativos | Ativo
  // (o app mostra as categorias na ordem das linhas da aba; sem número, ficam no fim, na ordem em que vieram)
  const ordemCat = (l) => (Number(l[0]) > 0 ? Number(l[0]) : 1e6);
  acrescentar(ABA_CATEGORIAS, 1, linhas("Categorias", 4)
    .map((l, i) => [l, i]).sort((a, b) => ordemCat(a[0]) - ordemCat(b[0]) || a[1] - b[1])
    .map(([l]) => [l[1] || "Bov", l[2], l[3], "SIM"]));

  // Minerais: Mineral | Kg por saco | Nomes alternativos  →  Mineral | Nomes alternativos | Kg por saco | Ativo
  acrescentar(ABA_MINERAIS, 0, linhas("Minerais", 3).map((l) => [l[0], l[2], l[1] === "" ? "" : Number(String(l[1]).replace(",", ".")) || l[1], "SIM"]));

  // Medicamentos: Medicamento | Tipo | Unidade da dose | Nomes alternativos  →  Medicamento | Nomes alt. | Unidade | Ativo | Tipo
  acrescentar(ABA_MEDICAMENTOS, 0, linhas("Medicamentos", 4).map((l) => [l[0], l[3], l[2], "SIM", l[1]]));

  const msg = "Cadastro importado de \"" + cad.getName() + "\":\n" + relatorio.join("\n");
  Logger.log(msg);
  return msg;
}

// Compartilha a planilha conforme a coluna Acesso do cadastro (o Google avisa a pessoa por e-mail).
// Nunca rebaixa nem retira um acesso que a pessoa já tem: isso fica no botão Compartilhar.
function compartilharPlanilha_(ss, usuarios, relatorio) {
  const emails = (lista) => lista.map((u) => String(u.getEmail()).toLowerCase());
  const dono = String(Session.getEffectiveUser().getEmail() || "").toLowerCase(); // quem roda (dono da planilha)
  const editores = emails(ss.getEditors());
  const leitores = emails(ss.getViewers());
  const feitos = [], ja = [], erros = [];
  usuarios.forEach((l) => {
    const acesso = norm_(l[3]);
    if (acesso.indexOf("planilha") < 0 && acesso !== "sim") return; // Só o app
    const email = l[1].toLowerCase();
    const editor = !/visualiz|leitor|ver\b/.test(acesso); // "App e planilha" sem detalhe = editor
    if (email === dono || editores.indexOf(email) >= 0 || (!editor && leitores.indexOf(email) >= 0)) { ja.push(email); return; }
    try {
      if (editor) ss.addEditor(email); else ss.addViewer(email);
      feitos.push(email + (editor ? " (editor)" : " (só visualização)"));
    } catch (e) {
      erros.push(email + ": " + e.message);
    }
  });
  if (feitos.length) relatorio.push("Planilha compartilhada com: " + feitos.join(", "));
  if (ja.length) relatorio.push("Já tinham acesso à planilha: " + ja.join(", "));
  if (erros.length) relatorio.push("ATENÇÃO, não foi possível compartilhar: " + erros.join("; "));
  if (!feitos.length && !ja.length && !erros.length) relatorio.push("Planilha: ninguém marcado com \"App e planilha\".");
}

// Grava um valor na aba Configuração (cria a chave se não existir)
function definirConfig_(chave, valor) {
  const sh = abaConfiguracao_();
  const l = sh.getRange(2, 1, sh.getLastRow() - 1, 1).getValues().findIndex((x) => norm_(x[0]) === norm_(chave));
  if (l >= 0) sh.getRange(l + 2, 2).setValue(valor);
  else sh.appendRow([chave, valor, ""]);
}
