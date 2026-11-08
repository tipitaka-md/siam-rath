# Syāmaraṭṭha Tepiṭakaṃ (Siam Rath Edition) in Markdown

This repository contains the complete 45-volume **Royal Thai Siam Rath (ฉบับสยามรัฐ / Syāmaraṭṭhassa Tepiṭakaṃ)** edition of the Pāḷi Tipiṭaka in **IAST Pali Roman** script converted to Markdown.

The source text is maintained in SQL format by [kit119/D-tipitaka](https://github.com/kit119/D-tipitaka) (`1.2/pali_siam.sql.bz2`), originally published under King Prajadhipok (Rama VII) in 1925–1928 (B.E. 2468–2471) in 45 volumes symbolizing the 45 years of the Buddha's ministry.

---

## Corpus & Directory Structure

All 45 volumes (covering **21,915 printed pages** and **17,090 textual variant footnotes**) are organized into Piṭaka and Nikāya folders:

```text
.
├── vinaya/                   # Vinayapiṭaka (Volumes 1–8)
│   ├── vol01.md              # Mahāvibhaṅga 1 (Pārājikakaṇḍa)
│   ├── vol02.md              # Mahāvibhaṅga 2 (Pācittiyakaṇḍa)
│   ├── vol03.md              # Bhikkhunīvibhaṅga
│   ├── vol04.md              # Mahāvagga 1
│   ├── vol05.md              # Mahāvagga 2
│   ├── vol06.md              # Cullavagga 1
│   ├── vol07.md              # Cullavagga 2
│   └── vol08.md              # Parivāra
│
├── sutta/                    # Suttantapiṭaka (Volumes 9–33)
│   ├── dn/                   # Dīghanikāya (Volumes 9–11)
│   │   ├── vol09.md          # Sīlakkhandhavagga
│   │   ├── vol10.md          # Mahāvagga
│   │   └── vol11.md          # Pāthikavagga
│   ├── mn/                   # Majjhimanikāya (Volumes 12–14)
│   │   ├── vol12.md          # Mūlapaṇṇāsa
│   │   ├── vol13.md          # Majjhimapaṇṇāsa
│   │   └── vol14.md          # Uparipaṇṇāsa
│   ├── sn/                   # Saṃyuttanikāya (Volumes 15–19)
│   │   ├── vol15.md          # Sagāthavagga
│   │   ├── vol16.md          # Nidānavagga
│   │   ├── vol17.md          # Khandhavagga
│   │   ├── vol18.md          # Saḷāyatanavagga
│   │   └── vol19.md          # Mahāvagga
│   ├── an/                   # Aṅguttaranikāya (Volumes 20–24)
│   │   ├── vol20.md          # Ekaka-, Duka-, Tikanipāta
│   │   ├── vol21.md          # Catukkanipāta
│   │   ├── vol22.md          # Pañcaka-, Chakkanipāta
│   │   ├── vol23.md          # Sattaka-, Aṭṭhaka-, Navakanipāta
│   │   └── vol24.md          # Dasaka-, Ekādasakanipāta
│   └── kn/                   # Khuddakanikāya (Volumes 25–33)
│       ├── vol25.md          # Khp, Dhp, Ud, Iti, Snp
│       ├── vol26.md          # Vv, Pv, Thag, Thig
│       ├── vol27.md          # Jātaka 1
│       ├── vol28.md          # Jātaka 2
│       ├── vol29.md          # Mahāniddesa
│       ├── vol30.md          # Cūḷaniddesa
│       ├── vol31.md          # Paṭisambhidāmagga
│       ├── vol32.md          # Apadāna 1
│       └── vol33.md          # Apadāna 2, Buddhavaṃsa, Cariyāpiṭaka
│
├── abhidhamma/               # Abhidhammapiṭaka (Volumes 34–45)
│   ├── vol34.md              # Dhammasaṅgaṇī
│   ├── vol35.md              # Vibhaṅga
│   ├── vol36.md              # Dhātukathā & Puggalapaññatti
│   ├── vol37.md              # Kathāvatthu
│   ├── vol38.md              # Yamaka 1
│   ├── vol39.md              # Yamaka 2
│   ├── vol40.md              # Paṭṭhāna 1
│   ├── vol41.md              # Paṭṭhāna 2
│   ├── vol42.md              # Paṭṭhāna 3
│   ├── vol43.md              # Paṭṭhāna 4
│   ├── vol44.md              # Paṭṭhāna 5
│   └── vol45.md              # Paṭṭhāna 6
│
├── .github/workflows/
│   └── sync-upstream.yml     # Automated upstream sync GitHub Action
├── convert.py                # Deterministic conversion & sync script
└── README.md
```

---

## Document Formatting

* **Page Citations & Direct Anchors:** Each page from the print edition has an anchor `<a id="page-N"></a>` and sub-header `##### *[Siam Rath Page N]*` for exact citation matching.
* **Verses (Gāthās):** Preserves line breaks with trailing Markdown spaces (`  \n`).
* **Footnotes & Textual Variants:** Footnote markers in the text (`[^pN-1]`, `[^pN-2]`) link directly to the page's textual variants and readings in a structured `## Footnotes` section at the end of each volume.
* **Transliteration Standard:** Standard IAST Pali Roman diacritics (`ā`, `ī`, `ū`, `ṭ`, `ḍ`, `ṇ`, `ḷ`, `ñ`, `ṅ`, `ṃ`) converted using [Aksharamukha](https://www.aksharamukha.com/python).

---

## Running the Deterministic Converter

[`convert.py`](file:///Users/christie/Repositories/Pali/siam-rath/convert.py) is a standalone deterministic Python script using PEP 723 inline script metadata.

### 1. Sync and convert latest upstream changes
```bash
uv run --python 3.11 convert.py --sync
```
*(Automatically fetches/pulls `kit119/D-tipitaka:master`, checks file hashes in `.cache/manifest.json`, and updates only modified files).*

### 2. Convert from an existing local copy
```bash
uv run --python 3.11 convert.py --source /path/to/pali_siam.sql.bz2
```

### 3. Force rebuild all files
```bash
uv run --python 3.11 convert.py --force
```

### Command Line Flags:
* `--sync`: Automatically clone or pull latest master from the upstream repository.
* `--upstream-repo`: URL of the upstream repository (default: `https://github.com/kit119/D-tipitaka.git`).
* `--upstream-dir`: Local storage directory for upstream checkout (default: `.cache/D-tipitaka`).
* `--source`: Path to `pali_siam.sql.bz2`.
* `--output`: Output directory for generated Markdown files (default: `.`).
* `--target`: Target script (default: `IASTPali`).
* `--force`: Force complete rebuild, bypassing SHA-256 cache.
* `--workers`: Parallel worker count (defaults to CPU count).
* `--limit`: Limit number of volumes to process.

---

## Continuous Sync (GitHub Actions)

A GitHub Actions workflow is provided at [`.github/workflows/sync-upstream.yml`](file:///Users/christie/Repositories/Pali/siam-rath/.github/workflows/sync-upstream.yml). It runs on a weekly schedule (and can be triggered manually via `workflow_dispatch`), syncing with upstream changes and committing updates automatically.
