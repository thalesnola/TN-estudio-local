#!/usr/bin/env python3
"""Exercise personal ArtCraft MCPs with synthetic images only (no user assets)."""
import asyncio
import base64
import io
import json
from pathlib import Path
import tempfile
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image

HOME = Path.home()
CONFIG = HOME/'.config/nola-macm5/artcraft'

async def call(session, tool, args):
    result = await session.call_tool(tool, args)
    messages = [c.text for c in result.content if c.type == 'text']
    if result.isError:
        raise RuntimeError(tool+': '+' '.join(messages)[:500])
    if tool == 'page_render':
        images = [c for c in result.content if c.type == 'image']
        if not images:
            raise RuntimeError('PDF render returned no image')
        with Image.open(io.BytesIO(base64.b64decode(images[0].data))) as image:
            image.verify()
    values = []
    for message in messages:
        try:
            values.append(json.loads(message))
        except ValueError:
            values.append(message)
    print(tool, json.dumps(values, ensure_ascii=False)[:400], flush=True)
    return values[0] if len(values) == 1 else values

async def exercise(app, entry, folder):
    if app == 'lightcraft':
        entry = {**entry, 'args':['mcp','--library',str(folder/'library'),'--compact']}
    async with stdio_client(StdioServerParameters(command=entry['command'], args=entry['args'])) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if app == 'photocraft':
                await call(session, 'doc_new', {'width':64,'height':64,'name':'nola-macm5','background':'#2468ac'})
                await call(session, 'doc_export', {'path':str(folder/'photo.png')})
            elif app == 'vectorcraft':
                await call(session, 'draw_shape', {'shape':'rectangle','x':10,'y':10,'width':40,'height':40,'fill':'#2468ac','name':'nola-macm5'})
                await call(session, 'export', {'path':str(folder/'vector.png'),'format':'png'})
                await call(session, 'export', {'path':str(folder/'vector.pdf'),'format':'pdf'})
            elif app == 'effectcraft':
                await call(session, 'describe_command', {'command':'comp.new'})
                await call(session, 'execute_command', {'command':'comp.new','params':{'name':'nola-macm5','width':64,'height':64,'duration':1,'frameRate':12}})
                await call(session, 'render_frame', {'path':str(folder/'effect.png'),'max_side':64,'inline':False})
            elif app == 'pdfcraft':
                opened = await call(session, 'doc_open', {'path':str(folder/'vector.pdf')})
                doc = opened.get('doc', opened.get('id', 1))
                await call(session, 'doc_info', {'doc':doc})
                await call(session, 'page_render', {'doc':doc,'page':1,'dpi':36})
            elif app == 'lightcraft':
                await call(session, 'import', {'paths':[str(folder/'photo.png')], 'mode':'add'})
                await call(session, 'render_photo', {'size':64,'path':str(folder/'light.png')})
            elif app == 'filmcraft':
                await call(session, 'media_import', {'paths':[str(folder/'photo.png')]})
                await call(session, 'project_inspect', {})
            elif app == 'designcraft':
                await call(session, 'new_document', {'title':'nola-macm5','width':64,'height':64,'pages':1,'margins':0})
                await call(session, 'export_png', {'path':str(folder/'design.png'),'scale':1})
            return {'status':'ok'}

async def main():
    servers = json.loads((CONFIG/'mcp.json').read_text())['mcpServers']
    root = HOME/'nola-macm5/midia/saida'
    root.mkdir(parents=True,exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix='nola-macm5-smoke-',dir=root))
    results = {}
    for name,entry in servers.items():
        app = name.removeprefix('nola-macm5-')
        try:
            results[app] = await asyncio.wait_for(exercise(app,entry,folder),timeout=60)
            print(app,'OK',flush=True)
        except Exception as error:
            results[app] = {'status':'error','message':str(error)}
            print(app,'FAILED',str(error),flush=True)
    for filename in ('photo.png','vector.png','effect.png','light.png','design.png'):
        if not (folder/filename).is_file():
            raise RuntimeError('Expected artifact missing: '+filename)
    for file in folder.glob('*.png'):
        with Image.open(file) as img:
            img.verify()
    (folder/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('ARTIFACTS',folder,flush=True)
    if any(e['status']!='ok' for e in results.values()):
        raise SystemExit(1)

if __name__ == '__main__':
    asyncio.run(main())
