# /// script
# requires-python = ">=3.9, <3.14"
# dependencies = [
#     "aksharamukha",
# ]
# ///
"""
Deterministic Siam Rath (Syāmaraṭṭha) Tipiṭaka SQL to Markdown Converter.

Transliterates Pāḷi text from Thai script to IAST Pali Roman using Aksharamukha.
Extracts the 45-volume Siam Rath Pali Canon from pali_siam.sql.bz2.

Source: https://github.com/kit119/D-tipitaka (1.2/pali_siam.sql.bz2)
Transliteration: https://www.aksharamukha.com/python
"""

import argparse
import bz2
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed

# Suppress regex escape warnings from older library dependencies
warnings.filterwarnings('ignore', category=SyntaxWarning)

from aksharamukha import transliterate

DEFAULT_UPSTREAM_URL = "https://github.com/kit119/D-tipitaka.git"
DEFAULT_UPSTREAM_DIR = ".cache/D-tipitaka"
MANIFEST_FILE = ".cache/manifest.json"

THAI_TO_ARABIC = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')

VOLUME_INFO = {
    1: ("vinaya", "Vinayapiṭake Mahāvibhaṅgassa Paṭhamo Bhāgo (Pārājikakaṇḍa)"),
    2: ("vinaya", "Vinayapiṭake Mahāvibhaṅgassa Dutiyo Bhāgo (Pācittiyakaṇḍa)"),
    3: ("vinaya", "Vinayapiṭake Bhikkhunīvibhaṅgo"),
    4: ("vinaya", "Vinayapiṭake Mahāvaggassa Paṭhamo Bhāgo"),
    5: ("vinaya", "Vinayapiṭake Mahāvaggassa Dutiyo Bhāgo"),
    6: ("vinaya", "Vinayapiṭake Cullavaggassa Paṭhamo Bhāgo"),
    7: ("vinaya", "Vinayapiṭake Cullavaggassa Dutiyo Bhāgo"),
    8: ("vinaya", "Vinayapiṭake Parivāro"),
    9: (os.path.join("sutta", "dn"), "Suttantapiṭake Dīghanikāyassa Sīlakkhandhavaggo"),
    10: (os.path.join("sutta", "dn"), "Suttantapiṭake Dīghanikāyassa Mahāvaggo"),
    11: (os.path.join("sutta", "dn"), "Suttantapiṭake Dīghanikāyassa Pāthikavaggo"),
    12: (os.path.join("sutta", "mn"), "Suttantapiṭake Majjhimanikāyassa Mūlapaṇṇāso"),
    13: (os.path.join("sutta", "mn"), "Suttantapiṭake Majjhimanikāyassa Majjhimapaṇṇāso"),
    14: (os.path.join("sutta", "mn"), "Suttantapiṭake Majjhimanikāyassa Uparipaṇṇāso"),
    15: (os.path.join("sutta", "sn"), "Suttantapiṭake Saṃyuttanikāyassa Sagāthavaggo"),
    16: (os.path.join("sutta", "sn"), "Suttantapiṭake Saṃyuttanikāyassa Nidānavaggo"),
    17: (os.path.join("sutta", "sn"), "Suttantapiṭake Saṃyuttanikāyassa Khandhavaggo"),
    18: (os.path.join("sutta", "sn"), "Suttantapiṭake Saṃyuttanikāyassa Saḷāyatanavaggo"),
    19: (os.path.join("sutta", "sn"), "Suttantapiṭake Saṃyuttanikāyassa Mahāvaggo"),
    20: (os.path.join("sutta", "an"), "Suttantapiṭake Aṅguttaranikāyassa (Ekaka-Duka-Tikanipāto)"),
    21: (os.path.join("sutta", "an"), "Suttantapiṭake Aṅguttaranikāyassa (Catukkanipāto)"),
    22: (os.path.join("sutta", "an"), "Suttantapiṭake Aṅguttaranikāyassa (Pañcaka-Chakkanipāto)"),
    23: (os.path.join("sutta", "an"), "Suttantapiṭake Aṅguttaranikāyassa (Sattaka-Aṭṭhaka-Navakanipāto)"),
    24: (os.path.join("sutta", "an"), "Suttantapiṭake Aṅguttaranikāyassa (Dasaka-Ekādasakanipāto)"),
    25: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa (Khuddakapāṭha, Dhammapada, Udāna, Itivuttaka, Suttanipāta)"),
    26: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa (Vimānavatthu, Petavatthu, Theragāthā, Therīgāthā)"),
    27: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa Jātakaṃ (Paṭhamo Bhāgo)"),
    28: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa Jātakaṃ (Dutiyo Bhāgo)"),
    29: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa Mahāniddeso"),
    30: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa Cūḷaniddeso"),
    31: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa Paṭisambhidāmaggo"),
    32: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa Apadānaṃ (Paṭhamo Bhāgo)"),
    33: (os.path.join("sutta", "kn"), "Suttantapiṭake Khuddakanikāyassa Apadānaṃ (Dutiyo Bhāgo), Buddhavaṃso, Cariyāpiṭakaṃ"),
    34: ("abhidhamma", "Abhidhammapiṭake Dhammasaṅgaṇī"),
    35: ("abhidhamma", "Abhidhammapiṭake Vibhaṅgo"),
    36: ("abhidhamma", "Abhidhammapiṭake Dhātukathā & Puggalapaññatti"),
    37: ("abhidhamma", "Abhidhammapiṭake Kathāvatthu"),
    38: ("abhidhamma", "Abhidhammapiṭake Yamakaṃ (Paṭhamo Bhāgo)"),
    39: ("abhidhamma", "Abhidhammapiṭake Yamakaṃ (Dutiyo Bhāgo)"),
    40: ("abhidhamma", "Abhidhammapiṭake Paṭṭhānaṃ (Paṭhamo Bhāgo)"),
    41: ("abhidhamma", "Abhidhammapiṭake Paṭṭhānaṃ (Dutiyo Bhāgo)"),
    42: ("abhidhamma", "Abhidhammapiṭake Paṭṭhānaṃ (Tatiyo Bhāgo)"),
    43: ("abhidhamma", "Abhidhammapiṭake Paṭṭhānaṃ (Catuttho Bhāgo)"),
    44: ("abhidhamma", "Abhidhammapiṭake Paṭṭhānaṃ (Pañcamo Bhāgo)"),
    45: ("abhidhamma", "Abhidhammapiṭake Paṭṭhānaṃ (Chaṭṭho Bhāgo)"),
}

def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def sync_upstream_repo(repo_url, target_dir):
    os.makedirs(os.path.dirname(os.path.abspath(target_dir)), exist_ok=True)
    if os.path.exists(os.path.join(target_dir, '.git')):
        print(f"Syncing existing upstream repo at {target_dir}...")
        subprocess.run(["git", "-C", target_dir, "fetch", "origin", "master"], check=True)
        subprocess.run(["git", "-C", target_dir, "checkout", "master"], check=True)
        subprocess.run(["git", "-C", target_dir, "pull", "--ff-only", "origin", "master"], check=True)
    else:
        print(f"Cloning upstream repo from {repo_url} into {target_dir}...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, target_dir], check=True)

    git_hash = subprocess.check_output(
        ["git", "-C", target_dir, "rev-parse", "HEAD"], text=True
    ).strip()
    print(f"Upstream is at commit: {git_hash}")
    return git_hash

def translit_pali(text, target='IASTPali'):
    if not text:
        return ''
    return transliterate.process(
        'Thai',
        target,
        text,
        post_options=['capitalizeSentence']
    )

def get_rel_path(vol_num):
    sec, _ = VOLUME_INFO.get(vol_num, ("misc", f"Volume {vol_num}"))
    return os.path.join(sec, f'vol{vol_num:02d}.md')

def convert_volume(vol_num, pages_data, output_root, target='IASTPali'):
    rel_path = get_rel_path(vol_num)
    out_path = os.path.join(output_root, rel_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    sec, title = VOLUME_INFO.get(vol_num, ("misc", f"Volume {vol_num}"))

    lines = []
    lines.append(f'# {title}\n')
    lines.append(f'> **Source:** Syāmaraṭṭhassa Tepiṭakaṃ (Siam Rath Edition, Volume {vol_num})')
    lines.append(f'> **Edition:** Royal Thai Edition (King Rama VII)')
    lines.append('\n---\n')

    all_footnotes = []

    # Sort pages strictly ascending
    sorted_pages = sorted(pages_data, key=lambda x: x[0])

    for pnum, raw_content in sorted_pages:
        lines.append(f'\n<!-- Siam Rath Page {pnum} -->\n<a id="page-{pnum}"></a>\n')
        lines.append(f'##### *[Siam Rath Page {pnum}]*\n')

        # Split body and footnotes (marked by #)
        body = raw_content
        fn_section = ''
        if '#' in raw_content:
            idx = raw_content.rfind('#')
            body = raw_content[:idx].strip()
            fn_section = raw_content[idx+1:].strip()

        # Parse footnotes definitions
        fn_items = []
        if fn_section:
            fn_matches = re.findall(r'([๑-๙\d]+)\s*(.*?)(?=(?:[๑-๙\d]+\s*)|$)', fn_section)
            for d, c in fn_matches:
                num = d.translate(THAI_TO_ARABIC)
                t_fn = translit_pali(c, target).strip()
                fn_items.append((num, t_fn))

        # Substitute footnote markers in body text
        def sub_fn(m):
            d = m.group(1).translate(THAI_TO_ARABIC)
            return f'[^{pnum}-{d}]'

        body = re.sub(r'([๑-๙])(?=[ก-ฮ\s])', sub_fn, body)

        # Transliterate body text
        t_body = translit_pali(body, target)

        # Format body lines
        body_lines = t_body.split('\n')
        para_buf = []

        for bline in body_lines:
            sline = bline.strip()
            if not sline:
                if para_buf:
                    lines.append('\n'.join(para_buf) + '\n')
                    para_buf = []
                continue

            # Check if line looks like a header/centered
            if sline.startswith('___'):
                continue
            if sline.startswith('Namo tassa') or 'Bhāgo' in sline or 'Vaggo' in sline or 'Kaṇḍaṃ' in sline:
                if para_buf:
                    lines.append('\n'.join(para_buf) + '\n')
                    para_buf = []
                lines.append(f'<p align="center">{sline}</p>\n')
            elif sline.endswith('.'):
                # End of verse line or paragraph
                para_buf.append(sline)
                lines.append('  \n'.join(para_buf) + '\n')
                para_buf = []
            else:
                # Continuing verse line
                para_buf.append(f'{sline}  ')

        if para_buf:
            lines.append('\n'.join(para_buf) + '\n')

        # Save footnotes
        for num, content in fn_items:
            all_footnotes.append((f'p{pnum}-{num}', content))

    if all_footnotes:
        lines.append('\n---\n\n## Footnotes\n')
        for fn_id, fn_text in all_footnotes:
            lines.append(f'[^{fn_id}]: {fn_text}')
        lines.append('')

    content = '\n'.join(lines)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as out_f:
        out_f.write(content)

    return rel_path, len(sorted_pages), len(all_footnotes)

def worker_task(args):
    vol_num, pages_data, output_root, target = args
    return convert_volume(vol_num, pages_data, output_root, target)

def load_manifest(manifest_path):
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_manifest(manifest_path, manifest_data):
    os.makedirs(os.path.dirname(os.path.abspath(manifest_path)), exist_ok=True)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2, sort_keys=True)

def parse_sql_file(sql_path):
    """Parse bz2 compressed SQL file and group by volume."""
    print(f"Reading {sql_path}...")
    volumes = {}
    opener = bz2.open if sql_path.endswith('.bz2') else open

    with opener(sql_path, 'rt', encoding='utf-8', errors='replace') as f:
        buf = []
        in_rec = False
        cur_vol = None
        cur_page = None

        for line in f:
            m = re.match(r'INSERT INTO \"pali_siam\" VALUES\((\d+),(\d+),', line)
            if m:
                in_rec = True
                cur_vol = int(m.group(1))
                cur_page = int(m.group(2))
                buf = [line]
            elif in_rec:
                buf.append(line)

            if in_rec and line.endswith(');\n'):
                in_rec = False
                full_rec = ''.join(buf)
                parts = full_rec.split("','", 1)
                if len(parts) > 1:
                    content = parts[1].rsplit("');", 1)[0]
                    content = content.replace("''", "'")
                    volumes.setdefault(cur_vol, []).append((cur_page, content))

    return volumes

def main():
    parser = argparse.ArgumentParser(
        description='Deterministic converter: Siam Rath (Thai) Pali Canon -> IAST Pali Roman Markdown'
    )
    parser.add_argument('--sync', action='store_true', help='Sync/pull latest master from upstream Git repository')
    parser.add_argument('--upstream-repo', default=DEFAULT_UPSTREAM_URL, help='Upstream git repository URL')
    parser.add_argument('--upstream-dir', default=DEFAULT_UPSTREAM_DIR, help='Local directory for upstream repository')
    parser.add_argument('--source', default=None, help='Explicit path to pali_siam.sql.bz2')
    parser.add_argument('--output', default='.', help='Output directory for generated markdown files')
    parser.add_argument('--target', default='IASTPali', help='Target transliteration script (default: IASTPali)')
    parser.add_argument('--force', action='store_true', help='Force full rebuild, ignoring cache')
    parser.add_argument('--manifest', default=MANIFEST_FILE, help='Path to manifest cache file')
    parser.add_argument('--workers', type=int, default=os.cpu_count() or 4, help='Number of parallel workers')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of volumes to process')

    args = parser.parse_args()

    upstream_commit = None
    if args.sync:
        upstream_commit = sync_upstream_repo(args.upstream_repo, args.upstream_dir)
    elif not os.path.exists(args.upstream_dir):
        if os.path.exists('/tmp/D-tipitaka'):
            args.upstream_dir = '/tmp/D-tipitaka'
        else:
            upstream_commit = sync_upstream_repo(args.upstream_repo, args.upstream_dir)

    source_path = args.source
    if not source_path:
        candidate = os.path.join(args.upstream_dir, '1.2', 'pali_siam.sql.bz2')
        if os.path.exists(candidate):
            source_path = candidate
        elif os.path.exists('/tmp/D-tipitaka/1.2/pali_siam.sql.bz2'):
            source_path = '/tmp/D-tipitaka/1.2/pali_siam.sql.bz2'

    if not source_path or not os.path.exists(source_path):
        print(f"Error: Source file {source_path} not found. Run with --sync or provide --source.")
        sys.exit(1)

    source_hash = compute_sha256(source_path)
    manifest = load_manifest(args.manifest)

    if not args.force and manifest.get('source_sha256') == source_hash and manifest.get('target') == args.target:
        print("All 45 volumes are up to date with upstream. Nothing to convert.")
        return

    volumes = parse_sql_file(source_path)
    vol_nums = sorted(volumes.keys())

    if args.limit:
        vol_nums = vol_nums[:args.limit]

    print(f"Starting conversion of {len(vol_nums)} volumes to {args.target} using {args.workers} workers...")
    t0 = time.time()

    tasks = [(v, volumes[v], args.output, args.target) for v in vol_nums]
    total_pages = 0
    total_notes = 0

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(worker_task, t): t[0] for t in tasks}
        completed = 0
        for fut in as_completed(futures):
            completed += 1
            rel_path, p_count, n_count = fut.result()
            total_pages += p_count
            total_notes += n_count
            elapsed = time.time() - t0
            print(f"[{completed}/{len(vol_nums)}] ({elapsed:.1f}s) Converted {rel_path} ({p_count} pages, {n_count} notes)")

    manifest['source_sha256'] = source_hash
    manifest['source_file'] = os.path.basename(source_path)
    if upstream_commit:
        manifest['upstream_commit'] = upstream_commit
    manifest['last_run'] = int(time.time())
    manifest['target'] = args.target

    save_manifest(args.manifest, manifest)

    total_time = time.time() - t0
    print(f"\nSuccessfully converted {len(vol_nums)} volumes in {total_time:.2f}s.")
    print(f"Total pages: {total_pages}, footnotes: {total_notes}")
    print(f"Manifest cache updated at {args.manifest}.")

if __name__ == '__main__':
    main()
