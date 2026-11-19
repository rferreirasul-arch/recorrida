/**
 * Recorrida — cópia diária no Dropbox (OPCIONAL; hoje só a Santa Rita usa).
 * Cole como segundo arquivo no Apps Script da planilha, junto com o Ponte.gs.
 * Na aba Configuração, acrescente as linhas "Pasta Dropbox" e "Arquivo Dropbox"
 * (Chave | Valor). Passo a passo da conexão: LEIA-ME.md do repositório, seção Dropbox.
 */
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
