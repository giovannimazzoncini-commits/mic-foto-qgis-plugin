# MIC_FOTO 0.2.4

Plugin sperimentale per QGIS 3.34-3.x (Qt5).

## Correzione 0.2.4
Il segnale clicked(bool) non viene piu inoltrato ai comandi senza argomenti browse, link_layer, stop_tool ed export. Gli argomenti di closeEvent e dei segnali di selezione restano invariati. Non vengono nascosti i TypeError interni ai metodi. Verificati con oggetti simulati i comandi con/senza checked e la conservazione degli altri argomenti; nessun test Qt/QGIS eseguito in questo ambiente.
Titoli del pannello e della galleria aggiornati alla 0.2.4. Conservati grafica 0.2.3, navigazione nella foto ingrandita e controlli sugli oggetti eliminati.

## Aggiornamento
Salvare sessione e progetto. Ricaricare il repository nel gestore plugin e verificare versione disponibile 0.2.4 prima di aggiornare. Riavviare QGIS dopo l'aggiornamento. Repository:
https://raw.githubusercontent.com/giovannimazzoncini-commits/mic-foto-qgis-plugin/main/plugins.xml
Attendere la generazione automatica di mic_foto.zip e plugins.xml. Abilitare i plugin sperimentali.

## Uso e limiti
Apri foto importa JPG/JPEG. Salva lavoro attiva la sessione JSON; Apri lavoro la riprende. Consulta sulla mappa collega clic sul punto e foto. Usa layer foto selezionato richiede filepath e non modifica il layer originale. Esportare un nuovo GeoPackage per conservare modifiche e stile; controllare la barra di stato per errori di salvataggio dello stile. Galleria con Precedente/Successiva e frecce. Originali non modificati da GPS nelle copie.
Solo JPG/JPEG, niente GPX/HEIC. Percorsi assoluti: non spostare le foto. JSON e GeoPackage separati. Scansione sincrona, annullamento non persistente. Non modificare direttamente la tabella del layer di lavoro. Salvare prima di chiudere QGIS.

## Licenza
GPL-3.0-or-later, codice e icona originali. Il pacchetto contiene il testo GPL-3.
