#!/usr/bin/env python3
"""Install pinned native ArtCraft CLIs and configure personal nola-macm5 MCPs."""
import argparse
import concurrent.futures
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
HOME = Path.home()
INSTALL = HOME/'Applications/nola-macm5/ArtCraft'
CACHE = HOME/'.cache/nola-macm5/artcraft'
CONFIG = HOME/'.config/nola-macm5/artcraft'
WORK = HOME/'nola-macm5/midia'


def checked(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=45).strip()


def download(url, path):
    if path.exists():
        return
    part = path.with_suffix(path.suffix+'.part')
    try:
        with urllib.request.urlopen(url, timeout=120) as response, part.open('wb') as output:
            shutil.copyfileobj(response, output)
        part.replace(path)
    finally:
        part.unlink(missing_ok=True)


def install_one(item):
    app, entry = item
    if entry['repository'] != 'storytold/'+app:
        raise ValueError('Unexpected repository: '+app)
    if not entry['url'].startswith('https://github.com/storytold/'+app+'/releases/download/'):
        raise ValueError('Unexpected release URL: '+app)
    CACHE.mkdir(parents=True, exist_ok=True)
    archive = CACHE/entry['asset']
    download(entry['url'], archive)
    with archive.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    if digest != entry['sha256']:
        raise ValueError('Checksum mismatch; remove bad cache and retry: '+str(archive))
    # Compare the exact pinned asset against the publisher's checksum list as well.
    with urllib.request.urlopen(entry['checksums_url'], timeout=60) as response:
        sums = response.read().decode()
    published = {line.split()[-1].lstrip('*'): line.split()[0] for line in sums.splitlines() if len(line.split()) == 2}
    if published.get(entry['asset']) != digest:
        raise ValueError('Publisher checksum mismatch: '+app)
    target = INSTALL/app/entry['version']
    relative = Path(entry['asset'].removesuffix('.zip'))/(app+'-cli')
    binary = target/relative
    if not binary.exists():
        with zipfile.ZipFile(archive) as package:
            for member in package.infolist():
                name = Path(member.filename)
                if name.is_absolute() or '..' in name.parts:
                    raise ValueError('Unsafe archive member')
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=target.parent) as temp:
            checked('ditto', '-x', '-k', str(archive), temp)
            candidate = Path(temp)/relative
            checked('codesign', '--verify', '--strict', str(candidate))
            architectures = checked('lipo', '-archs', str(candidate))
            if 'arm64' not in architectures.split():
                raise ValueError('No arm64 slice: '+app)
            if target.exists():
                raise ValueError('Incomplete existing installation; inspect before replacing: '+str(target))
            shutil.move(temp, target)
    checked('codesign', '--verify', '--strict', str(binary))
    architecture = checked('lipo', '-archs', str(binary))
    if 'arm64' not in architecture.split():
        raise ValueError('Installed binary lacks arm64 slice: '+app)
    try:
        help_text = checked(str(binary), 'mcp', '--help')
    except subprocess.CalledProcessError:
        # LightCraft documents MCP options only in its top-level help.
        help_text = checked(str(binary), '--help')
    return app, {'binary': str(binary), 'version': entry['version'], 'sha256': digest,
                 'architectures': architecture, 'mcp_help': help_text}


def mcp_entry(app, binary, help_text, work):
    args = ['mcp']
    # Only pass capabilities confirmed by the pinned CLI; flags changed since Windows setup.
    if '--automation-read-root' in help_text and '--automation-write-root' in help_text:
        args += ['--automation-read-root', str(work), '--automation-write-root', str(work/'saida')]
    elif app == 'pdfcraft' and '--root' in help_text:
        args += ['--root', str(work)]
    elif app == 'lightcraft' and '--library' in help_text:
        args += ['--library', str(work/'biblioteca')]
    elif app in ('photocraft', 'vectorcraft', 'effectcraft', 'pdfcraft', 'lightcraft'):
        raise ValueError('Expected workspace flags absent: '+app)
    if app in ('pdfcraft', 'lightcraft') and '--compact' in help_text:
        args += ['--compact']
    return {'command': binary, 'args': args}


def save_json(path, data):
    content = json.dumps(data, indent=2, ensure_ascii=False)+'\n'
    if path.exists() and path.read_text() == content:
        return
    if path.exists():
        backup = CONFIG/'backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')/path.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(content)
    temp.chmod(0o600)
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='download and install; default prints plan')
    parser.add_argument('--register', action='store_true', help='register namespaced MCPs in Codex (requires --apply)')
    args = parser.parse_args()
    lock = json.loads((HERE/'artcraft.lock.json').read_text())
    if not args.apply:
        print(json.dumps({'install':str(INSTALL), 'work':str(WORK), 'versions':{a:e['version'] for a,e in lock.items()},'register':args.register}, indent=2))
        return
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise SystemExit('This variant requires macOS Apple Silicon.')
    if not (HOME/'nola-macm5').is_dir():
        raise SystemExit('Personal root nola-macm5 must exist before installation.')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        installed = dict(pool.map(install_one, lock.items()))
    for directory in (WORK/'entrada', WORK/'saida', WORK/'biblioteca'):
        directory.mkdir(parents=True, exist_ok=True)
    servers = {'nola-macm5-'+app: mcp_entry(app, e['binary'], e['mcp_help'], WORK) for app,e in installed.items()}
    save_json(CONFIG/'mcp.json', {'mcpServers':servers})
    save_json(CONFIG/'installed.json', installed)
    project_config = WORK/'.mcp.json'
    project_data = json.loads(project_config.read_text()) if project_config.exists() else {}
    project_data['mcpServers'] = {**project_data.get('mcpServers', {}), **servers}
    save_json(project_config, project_data)
    if args.register:
        codex_config = HOME/'.codex/config.toml'
        if codex_config.exists():
            backup = CONFIG/'backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')/'codex-config.toml'
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(codex_config, backup)
        for name, entry in servers.items():
            checked('codex', 'mcp', 'add', name, '--', entry['command'], *entry['args'])
    for app, entry in installed.items():
        print(app, entry['version'], entry['architectures'], 'signature and SHA-256 OK')
    print('MCP manifest: '+str(CONFIG/'mcp.json'))


if __name__ == '__main__':
    main()
