# MIC_FOTO 0.3.0

Restyling del solo pannello, mantenendo le funzioni della 0.2.5. Nessun percorso di sopralluogo, rete OSM, routing o nuova dipendenza.

## Interfaccia
Intestazione con icona e accento petrolio. Modalita e layer collegato in evidenza. Comandi di apertura e salvataggio compatti. Scheda Foto con elenco e anteprima ridimensionabili, navigazione, dettagli, Segui foto e Consulta sulla mappa. Scheda Posizionamento separata: comandi disabilitati durante la consultazione diretta di un GeoPackage. Menu Esporta nell'intestazione con Esporta GeoPackage e Scrivi GPS nelle copie. Stile applicato soltanto al corpo del plugin, non al tema generale QGIS.

## Uso
Apri foto importa JPG/JPEG; Salva lavoro conserva la sessione JSON. Apri lavoro riprende una sessione precedente. Usa layer selezionato consulta direttamente un layer di punti con filepath, senza duplicarlo e senza modificarne i dati. Ingrandisci foto mantiene navigazione con pulsanti e frecce. Il GeoPackage contiene collegamenti alle immagini: i JPG devono restare accessibili.

## Aggiornamento
Salvare lavoro e progetto. Ricaricare il repository nel gestore plugin, con sperimentali abilitati:
https://raw.githubusercontent.com/giovannimazzoncini-commits/mic-foto-qgis-plugin/main/plugins.xml
Verificare versione disponibile 0.3.0, aggiornare e riavviare QGIS. Il workflow genera mic_foto.zip e plugins.xml.

## Verifiche e limiti
Sintassi e controlli statici verificati; callback del menu simulate con checked True/False. Nessun test Qt/QGIS eseguito in questo ambiente: collaudare ridimensionamento, contrasto, esportazione dal menu, consultazione GeoPackage e posizionamento. Restano i limiti della 0.2.5: JPG/JPEG, niente GPX/HEIC, percorsi delle immagini da mantenere accessibili, sessione e GeoPackage separati. Il restyling riutilizza i controlli e i segnali esistenti, senza riscrivere geometrie o attributi.

## Licenza
GPL-3.0-or-later, codice e icona originali. Testo GPL-3 incluso nel pacchetto.
