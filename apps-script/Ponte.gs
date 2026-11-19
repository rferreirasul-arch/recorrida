/**
 * Recorrida — PONTE da planilha de uma propriedade.
 *
 * Este é o ÚNICO arquivo no Apps Script da planilha (Extensões > Apps Script).
 * Todo o resto fica na biblioteca "Recorrida Núcleo" (identificador: RecorridaNucleo).
 * Para atualizar o app: publique uma nova versão da biblioteca e, aqui, em
 * Bibliotecas > RecorridaNucleo, troque o número da versão. Não precisa reimplantar o App da Web.
 *
 * Primeira vez (passo a passo no Roteiro de implantação):
 *  1. Bibliotecas (+) > cole o ID do script "Recorrida Núcleo" > identificador RecorridaNucleo > última versão.
 *  2. Rode configurar.
 *  3. Cole o link do cadastro em CADASTRO_URL e rode importarCadastro.
 *  4. Implantar > Nova implantação > App da Web (Executar como: eu; Quem pode acessar: qualquer pessoa).
 */

// Link da planilha de cadastro da propriedade, já aberta no Google Planilhas (só para importarCadastro)
const CADASTRO_URL = "";

// Entrega à biblioteca os serviços DESTE script (propriedades do Dropbox, cache de login e trava)
function servicos_() {
  RecorridaNucleo.usarServicos({
    props: PropertiesService.getScriptProperties(),
    cache: CacheService.getScriptCache(),
    lock: LockService.getScriptLock(),
  });
  return RecorridaNucleo;
}

// App da Web
function doPost(e) { return servicos_().doPost(e); }
function doGet(e) { return servicos_().doGet(e); }

// Rode pelo editor
function configurar() { servicos_().configurar(); }
function importarCadastro() { servicos_().importarCadastro(CADASTRO_URL); }

// Painel: menu "Recorrida" e troca do período (B4)
function onOpen(e) {
  SpreadsheetApp.getUi().createMenu("Recorrida").addItem("Atualizar painel", "atualizarPainel").addToUi();
  try { atualizarPainel(); } catch (err) { console.warn("Painel: " + err); }
}
function onEdit(e) {
  if (e && e.range && e.range.getSheet().getName() === "Painel" && e.range.getA1Notation() === "B4") atualizarPainel();
}
function atualizarPainel() { servicos_().atualizarPainel(); }

// Cópia diária no Dropbox (pasta e arquivo: aba Configuração)
function dropboxConectar() { servicos_().dropboxConectar(); }
function exportarParaDropbox() { servicos_().exportarParaDropbox(); }
// O agendamento fica aqui (e não na biblioteca) para o gatilho ser desta planilha
function agendarExportacao() {
  ScriptApp.getProjectTriggers()
    .filter((t) => t.getHandlerFunction() === "exportarParaDropbox")
    .forEach((t) => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger("exportarParaDropbox").timeBased()
    .everyDays(1).atHour(5).nearMinute(0).inTimezone("America/Sao_Paulo").create();
  Logger.log("Exportação agendada para todo dia às 5h.");
}
