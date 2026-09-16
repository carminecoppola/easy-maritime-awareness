# Specifica campagna di acquisizione dati — EASY-v3

Riferimento risultati: `outputs/reports/easy_v3_results.md`.

## Priorità di raccolta

| Priorità | Cosa | Motivo |
| --- | --- | --- |
| Alta | Boe della zona operativa (tipo, colore, forma, condizioni di luce) | Solo 18 sequenze-boa totali oggi (5 EASY + 13 ABOships); recall su dominio mare aperto ancora ~4% |
| Alta | Mare aperto, oggetti piccoli/distanti | Gap isolato su MODD2: 956 ostacoli annotati, 37 trovati dal miglior modello |
| Media | Condizioni avverse (foschia, controluce, mare mosso) | Sotto-rappresentate in tutte le fonti attuali |
| Media | Falsi positivi del contesto reale (scafo proprio, moli con persone/oggetti) | Misurato solo su scene generiche finora (16.9% FP) |
| Da confermare | Classi `debris`, `person` | Nello schema originale (`configs/dataset_schema.yaml`), mai popolate |

## Da definire col team

- Modello/i di camera e ottica montati
- Risoluzione e frame rate target
- Zona/e geografica/e e stagionalità
- Tipo di boe/segnaletica della zona (sistema IALA A/B, colori locali)
- Numero di sequenze-boa target (riferimento minimo: 15-20)
- Formato di annotazione e strumento di labeling
- Budget di annotazione disponibile

## Requisito: sequence id esplicito

Ogni uscita/giornata/video deve avere un identificativo assegnato al momento
della raccolta, non ricostruito dopo. Manifest minimo per lotto:
`sequence_id, data, zona, condizioni, camera, numero frame`.

`scripts/dataset/build_sequence_safe_split.py` legge già un `manifest.csv`
(colonne `stem`/`filename`, `sequence_id`) se presente nel source-root.

## Formato di consegna

```
data/external_sources/<nome_lotto>_v1/
├── images/
├── labels/            # YOLO: class x_center y_center width height
├── manifest.csv        # stem, sequence_id
└── PROVENANCE.md        # data, zona, camera, licenza/proprietà
```

## Prossimi passi

1. Raccogliere le risposte alla sezione "Da definire col team".
2. Validare il primo lotto (anche piccolo) con lo stesso schema prima di
   procedere su larga scala.
