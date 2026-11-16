# MIC_FOTO 0.2.0

Plugin sperimentale per QGIS 3.34, Qt5. Non collaudato automaticamente dentro QGIS: verificare su copie delle foto. La base 0.1.0 e' stata provata dall'utente; la nuova interfaccia richiede collaudo.

## Installazione e aggiornamenti
Dopo il successo del workflow Publish QGIS plugin, aggiungere in QGIS, Plugin > Gestisci e installa plugin > Impostazioni > Aggiungi, il repository:
https://raw.githubusercontent.com/giovannimazzoncini-commits/mic-foto-qgis-plugin/main/plugins.xml
Abilitare Mostra anche plugin sperimentali. Cercare MIC_FOTO in Tutti o Aggiornabili, installare/aggiornare e riavviare QGIS dopo aver salvato il lavoro. Se il workflow fallisce, l'indice e il pacchetto potrebbero non essere aggiornati: controllare Actions su GitHub.

## Consultazione
Apri foto importa JPG/JPEG, anche nelle sottocartelle. Apri lavoro ricarica le sessioni JSON della 0.1.0 e 0.2.0. Salva lavoro attiva il salvataggio automatico delle posizioni successive.
Selezionare una foto o usare Precedente/Successiva: il punto viene selezionato sulla mappa. Con Segui foto attivo la mappa si centra mantenendo la scala. I filtri limitano la navigazione all'elenco visibile.
Consulta sulla mappa attiva lo strumento per cliccare i punti del layer di lavoro e aprire la foto. Selezioni QGIS sul layer di lavoro vengono sincronizzate. Collega layer attivo importa un layer con filepath (es. GPKG MIC_FOTO), crea un layer di lavoro separato e sincronizza anche la selezione del layer originale senza modificarlo. Le modifiche richiedono una nuova esportazione. Per riprendere il lavoro salvare anche la sessione JSON.
Anteprima ridimensionabile con divisore elenco/foto. Ingrandisci foto o doppio clic apre una finestra adattabile. Le etichette distinguono EXIF e posizione manuale; EXIF non certifica che la posizione provenga dal telefono.

## Modifica e salvataggio
Aprire Modifica posizione per abilitare i comandi. Posiziona / correggi assegna la posizione con clic sinistro; clic destro o Termina conclude. Annulla ultima posizione ripristina l'ultima modifica della sessione corrente.
Esporta GeoPackage salva tutti i record, anche senza geometria, in un nuovo file. GPS nelle copie crea JPG senza sovrascrivere nomi esistenti, rilegge i GPS e salva un rapporto JSON. Gli originali non sono modificati.

## Limiti
JPG/JPEG, niente GPX/HEIC. Percorsi assoluti: non spostare le immagini. Foto mancanti segnalate, ricollocamento cartelle non ancora implementato. Sessione JSON e GPKG sono separati. Scansione sincrona: cartelle grandi possono rallentare QGIS. Salvare prima di chiudere QGIS. Non modificare direttamente gli attributi del layer di lavoro: viene rigenerato dal pannello. Punti sovrapposti possono richiedere selezione tramite tabella o elenco.

## Collaudo consigliato
Provare importazione, selezione punto-foto e foto-punto, navigazione, filtri, anteprima, CRS diverso da WGS84, riapertura sessione 0.1.0, collegamento GPKG, modifica ed esportazione. Verificare su copie la scrittura EXIF. I controlli di sintassi e ZIP non sostituiscono i test dentro QGIS.

## Licenza
SPDX-License-Identifier: GPL-3.0-or-later. Codice originale; nessun sorgente di ImportPhotos o GeotagManager incluso. Il pacchetto prodotto dal workflow include il testo GPL-3 in mic_foto/LICENSE. Il motore 0.1.0 in plugin.py viene mantenuto come base; viewer.py aggiunge la nuova interfaccia.
