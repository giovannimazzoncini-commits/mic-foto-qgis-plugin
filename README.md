# MIC_FOTO 0.2.3

Plugin sperimentale per QGIS 3.34-3.x (Qt5).

## Novita
Icona SVG originale fotocamera bianca e posizione arancio su petrolio; pulsante toolbar solo icona con tooltip. Punti circolari petrolio con bordo bianco, rombi arancio per source=manual. EXIF indica la lettura dal file, non certifica una posizione registrata dal telefono. La foto corrente ha un anello bianco/arancio sulla mappa senza modificare i colori globali di selezione. Lo stile viene applicato al lavoro MIC_FOTO e ai nuovi GeoPackage esportati, non ai layer esterni collegati. Nei nuovi GeoPackage il plugin tenta di salvare lo stile predefinito e segnala eventuali errori nella barra di stato.
Restano navigazione nella foto ingrandita (pulsanti e frecce), sincronizzazione foto-punto, sessioni JSON e controlli della 0.2.1 sugli oggetti eliminati.

## Aggiornamento
Salvare lavoro e progetto. Nel gestore plugin abilitare gli sperimentali e ricaricare il repository:
https://raw.githubusercontent.com/giovannimazzoncini-commits/mic-foto-qgis-plugin/main/plugins.xml
Verificare versione disponibile 0.2.3, aggiornare e riavviare QGIS. Attendere il completamento del workflow Publish QGIS plugin.

## Uso
Apri foto importa JPG/JPEG. Salva lavoro sceglie la sessione .micfoto.json e attiva il salvataggio delle successive posizioni. Apri lavoro riprende le sessioni precedenti. Usa layer foto selezionato carica il layer attivo con campo filepath senza modificarlo; esportare un nuovo GeoPackage per conservare le modifiche. Consulta sulla mappa apre la foto cliccando il punto. Precedente/Successiva e frecce nella galleria seguono il filtro; Segui foto mantiene la scala della mappa. Modifica posizione abilita assegnazione e annullamento. GPS nelle copie non modifica gli originali e non sovrascrive omonimi.

## Limiti e test
Solo JPG/JPEG, niente GPX/HEIC. Percorsi assoluti, non spostare le foto. Sessione e GeoPackage separati. Scansione sincrona, annullamento non persistente. Non modificare direttamente la tabella del layer di lavoro. Le personalizzazioni dello stile del lavoro MIC_FOTO possono essere sostituite quando viene rigenerato; quelle dei layer esterni non vengono alterate.
Controllati sintassi Python, SVG e regole con oggetti simulati. Non eseguiti test Qt/QGIS: verificare icona, punti, anello, esportazione e riapertura dello stile, galleria, rimozione layer e disattivazione su copie dei dati.

## Licenza
Codice e icona originali: GPL-3.0-or-later. Il pacchetto include il testo GPL-3 in mic_foto/LICENSE. Nessun sorgente di ImportPhotos o GeotagManager incluso.
