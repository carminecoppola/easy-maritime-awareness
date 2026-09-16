# EASY-v3 — risultati validazione e sviluppo dataset

## 1. Data leakage nello split ufficiale (EASY-v1-rgb3-buoy-rebalanced)

`easy_v1_buoy_rebalanced_split_assignments.csv` ha una colonna `sequence`
(gruppo video/blocco sorgente) che non è stata rispettata durante il
rebalancing delle boe: 1127 immagini spostate tra split per singola immagine,
ignorando la sequenza di appartenenza. Risultato: 11 sequenze su 36 divise
tra train/val/test (es. `smd:MVI_1469_VIS` presente in tutti e tre).

Spiega il salto anomalo di boat recall (0.43 val vs 0.88 test) e il gap tra
le metriche ufficiali e le prestazioni reali misurate sotto.

## 2. Falsi positivi su scene non marittime

124 immagini non marittime (COCO128 filtrato). 16.9% producono almeno un
falso positivo a soglia operativa (conf≥0.25), sempre classificato "ship"
(0 boat, 0 buoy). Esempio: letto a baldacchino classificato "ship" 0.83.

## 3. Validazione esterna su MODD2

482 frame campionati da MODD2 (28 sequenze, mai visto in training), 956
ostacoli annotati.

| Modello | Recall (class-agnostic, IoU 0.3) |
| --- | ---: |
| EASY-v1 ufficiale | 1.05% |
| EASY-v3 migliore (640+ABOships) | 3.87% |

Verificato non essere un artefatto di pipeline: box GT correttamente
allineati, veri positivi coerenti (es. gommone vicino rilevato), falsi
negativi sono ostacoli reali minuscoli/distanti sull'orizzonte.

## 4. Split sequence-safe

Nessuno script versionato costruiva lo split ufficiale (probabile notebook
rimosso). Ricostruito: `scripts/dataset/build_sequence_safe_split.py` —
raggruppa sempre per sequenza, mai per immagine, con audit di leakage
obbligatorio.

Supporta più sorgenti dati e, per raccolte future, un manifest esplicito di
sequenza (`manifest.csv`) invece di inferirla dal nome file.

## 5. Confronto training (stesso modello YOLOv8n, stessi iperparametri)

| | Ufficiale (leakage) | Sequence-safe, solo dati EASY | + ABOships, 640px | + ABOships, 960px |
| --- | ---: | ---: | ---: | ---: |
| Precision | 0.915 | 0.522 | 0.699 | 0.712 |
| Recall | 0.918 | 0.369 | 0.592 | 0.642 |
| mAP50 | 0.942 | 0.382 | 0.627 | 0.678 |
| mAP50-95 | 0.707 | 0.238 | 0.314 | 0.344 |
| Boat recall | — | 0.198 | — | 0.651 |
| Buoy recall | — | 0.000 | 0.485 | 0.536 |

ABOships (Zenodo 10.5281/zenodo.4736931, CC BY 4.0, Åbo Akademi): 9038
immagini, 13 sequenze, classe "seamark"→buoy verificata visivamente.
Mapping: boat/sailboat/motorboat/miscboat→boat,
cargoship/cruiseship/ferry/militaryship/passengership→ship, seamark→buoy.

## Verdetto

- Il numero ufficiale 0.942 mAP50 è un artefatto di leakage.
- Dati pubblici (ABOships) migliorano sostanzialmente le prestazioni nel
  dominio di training (boat recall ×3, buoy da 0 a 0.5+).
- Su dati di dominio realmente diverso (MODD2: mare aperto, oggetti
  piccoli/distanti) il miglioramento è marginale (1.05%→3.87%): i dati
  pubblici disponibili non coprono questo scenario.
- Risoluzione 960 vs 640: miglioramento reale ma modesto (+10% mAP50-95),
  non risolutivo.

**Conclusione**: serve raccolta dati proprietaria nel dominio operativo
specifico (mare aperto, oggetti piccoli, boe della zona). Specifica in
`docs/proprietary_acquisition_spec.md`.

## Riferimenti

- Split: `scripts/dataset/build_sequence_safe_split.py`
- Curation ABOships: `scripts/dataset/curate_aboships.py`
- Training: `scripts/validation/train_sequence_safe_candidate.py`
- Validazione esterna: `scripts/validation/modd2_external_eval.py`,
  `scripts/validation/false_positive_scan.py`
- Dataset candidato: `data/processed/EASY-v3-aboships-candidate/`
- Pesi migliori: `outputs/experiments/easy_v3_aboships_candidate/yolov8n_pretrained_50ep_easy_v3_aboships_candidate_960/weights/best.pt`
- Dati grezzi (JSON): `outputs/reports/easy_v1_modd2_external_eval.json`,
  `outputs/reports/easy_v1_false_positive_scan.json`,
  `outputs/reports/easy_v3_aboships960_modd2_external_eval.json`
