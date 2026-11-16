# MIC_FOTO 0.2.5

Plugin sperimentale per QGIS 3.34-3.x (Qt5).

## Consultazione diretta dei layer
Caricare il GeoPackage in QGIS, selezionare il layer fotografico e premere Usa layer foto selezionato. Il layer deve contenere punti singoli e il campo filepath. Non viene creato alcun nuovo layer temporaneo. Clic sui punti tramite Consulta sulla mappa, selezione QGIS, elenco e galleria sono sincronizzati sullo stesso layer usando i suoi FID. Non e richiesto il campo photo_id.
La modalita viene indicata nel pannello. Modifica posizione, assegnazione e annullamento sono bloccati: non vengono riscritti gli elementi del layer collegato. La simbologia originale viene conservata. Eventuali modifiche esterne al layer richiedono un nuovo collegamento per aggiornare l'elenco. Dopo il riavvio di QGIS ricollegare il layer; per la sola consultazione non serve aprire una sessione JSON.
Il GeoPackage contiene i percorsi delle fotografie, non incorpora i JPG. File mancanti segnalati nell'elenco. Percorsi relativi interpretati rispetto alla cartella della sorgente del layer o del progetto. Non vengono corretti automaticamente percorsi spostati.

## Altre modalita
Apri foto e Apri lavoro chiedono di scollegare il layer prima di aprire un altro lavoro. Le funzioni di importazione e posizionamento continuano a usare il lavoro MIC_FOTO. Salvare le sessioni JSON e i GeoPackage prima di chiudere. La galleria ingrandita mantiene Precedente/Successiva e frecce. Conservati icona, punti e controlli delle versioni precedenti.

## Aggiornamento
Salvare lavoro e progetto. Abilitare plugin sperimentali e ricaricare il repository:
https://raw.githubusercontent.com/giovannimazzoncini-commits/mic-foto-qgis-plugin/main/plugins.xml
Controllare versione disponibile 0.2.5, aggiornare e riavviare QGIS. Il workflow genera mic_foto.zip e plugins.xml.

## Test e limiti
Sintassi verificata e test simulati su collegamento allo stesso layer, FID non consecutivi senza photo_id, blocco della ricostruzione, selezione diretta e percorsi mancanti. Non eseguito collaudo Qt/QGIS in questo ambiente. Provare prima su copie dei dati. Solo JPG/JPEG, niente GPX/HEIC; scansione sincrona. Non modificare direttamente gli attributi del lavoro temporaneo.

## Licenza
GPL-3.0-or-later, codice e icona originali. Il pacchetto include il testo GPL-3.
