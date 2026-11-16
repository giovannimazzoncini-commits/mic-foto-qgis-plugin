# MIC_FOTO

Plugin sperimentale per QGIS 3.34 (Qt5), versione base 0.1.0.

## Funzioni
Importazione ricorsiva JPG/JPEG, lettura EXIF, anteprima, posizionamento sulla mappa, annullamento, sessioni JSON, esportazione GeoPackage e scrittura GPS nelle copie con verifica. Gli originali non vengono modificati.

## Uso
Aprire MIC_FOTO dal menu Plugin. Apri cartella importa le fotografie. Premere subito Salva lavoro per scegliere il file .micfoto.json: da quel momento le modifiche vengono salvate automaticamente. Selezionare una foto e Posiziona / correggi sulla mappa, quindi cliccare il punto di scatto. Terminare con clic destro o Termina posizionamento.

Apri lavoro riapre la sessione JSON, non il GeoPackage. Esporta GPKG crea un nuovo file con tutti i record; le foto senza posizione hanno geometria nulla. Scrivi GPS nelle copie crea nuovi JPG nella cartella scelta e un rapporto JSON; i nomi esistenti vengono saltati. Conservare sessione, foto e GeoPackage senza spostare le immagini (percorsi assoluti).

## Stato e limiti
0.1.0 collaudata dall'autore nella propria installazione QGIS; non e' una certificazione su tutte le piattaforme. Solo JPG/JPEG, niente GPX/HEIC, scansione sincrona, annullamento non persistente. Non importa GeoPackage come sessione. Salvare prima di chiudere QGIS. Non modificare il layer di lavoro dalla tabella attributi: viene rigenerato dal pannello.

La 0.2.0 con interfaccia migliorata e sincronizzazione bidirezionale foto-punto e' pianificata, non inclusa. Nessun pacchetto di distribuzione o indice plugins.xml e' ancora pubblicato.

## Sorgenti
La cartella mic_foto contiene il plugin. Per l'installazione manuale copiarla nella cartella dei plugin del profilo QGIS, quindi riavviare QGIS e attivare MIC_FOTO.

## Licenza
SPDX-License-Identifier: GPL-3.0-or-later. Codice originale; non include sorgenti di ImportPhotos o GeotagManager. Testo della licenza: https://www.gnu.org/licenses/gpl-3.0.txt . Aggiungere il testo integrale LICENSE prima di distribuire una release.
