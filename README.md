# MIC_FOTO 0.2.2

Plugin sperimentale per QGIS 3.34-3.x (Qt5). Il funzionamento richiede collaudo in QGIS; i controlli statici non equivalgono a test dell'interfaccia.

## Novita 0.2.2
- Ingrandisci foto apre una finestra non modale: la mappa resta utilizzabile.
- Pulsanti Precedente/Successiva e frecce sinistra/destra nella finestra ingrandita; Esc chiude la finestra.
- Navigazione sincronizzata con elenco e punto selezionato. Rispetta il filtro corrente e Segui foto sulla mappa.
- Dimensione della finestra mantenuta durante la navigazione e la riapertura nella stessa sessione.
- Collega layer attivo rinominato Usa layer foto selezionato, con spiegazione.
- Conservati i controlli della 0.2.1 sugli oggetti Qt eliminati e il pacchetto mic_foto.zip.

## Installazione
In Plugin > Gestisci e installa plugin > Impostazioni, aggiungere il repository:
https://raw.githubusercontent.com/giovannimazzoncini-commits/mic-foto-qgis-plugin/main/plugins.xml
Abilitare i plugin sperimentali, ricaricare i repository e verificare la versione disponibile 0.2.2 prima di aggiornare. Salvare lavoro e progetto e riavviare QGIS dopo l'aggiornamento. Il workflow Publish QGIS plugin deve completare la generazione del pacchetto e dell'indice.

## Uso
Apri foto importa JPG/JPEG anche dalle sottocartelle. Salva lavoro sceglie una sessione .micfoto.json e attiva il salvataggio delle modifiche successive. Apri lavoro riprende le sessioni precedenti.
Selezionare una foto o usare Precedente/Successiva seleziona il punto. Consulta sulla mappa permette di cliccare un punto per aprire la fotografia. Segui foto sulla mappa centra la vista mantenendo la scala.
Ingrandisci foto o doppio clic sull'anteprima apre la galleria. Navigazione ai limiti disabilitata, senza ricominciare automaticamente dall'altra estremita.
Usa layer foto selezionato importa il layer attivo con campo filepath, ad esempio un GeoPackage MIC_FOTO, creando un lavoro separato. Il layer originale non viene modificato; esportare un nuovo GeoPackage per conservare le correzioni.
Modifica posizione abilita posizionamento e annullamento. Clic sinistro assegna, clic destro o Termina interrompe. Esporta GeoPackage include tutte le foto, anche senza geometria. GPS nelle copie scrive e verifica i geotag senza modificare gli originali; gli omonimi vengono saltati e viene creato un rapporto JSON.

## Limiti e collaudo
Solo JPG/JPEG; niente GPX/HEIC. Percorsi assoluti: non spostare le foto. Sessione JSON e GeoPackage separati. Scansione sincrona; annullamento non persistente. Salvare prima di chiudere QGIS. Non modificare direttamente la tabella del layer di lavoro.
Verificare galleria con prima/ultima foto, filtri, frecce, ridimensionamento, file mancante, selezione sulla mappa mentre la galleria e aperta, salvataggio e riapertura. Verificare anche la rimozione del layer e la disattivazione del plugin. Non eseguiti test automatici dentro QGIS in questo ambiente.

## Licenza
SPDX-License-Identifier: GPL-3.0-or-later. Codice originale; nessun sorgente di ImportPhotos o GeotagManager incluso. Il pacchetto generato include il testo GPL-3 in mic_foto/LICENSE.
