#!/usr/bin/env python3
"""Initialize the installed personal MCPs and save their tool schemas locally."""
import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def inspect(name, entry):
    params = StdioServerParameters(command=entry['command'], args=entry['args'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            result = await session.list_tools()
            return {'server': initialized.serverInfo.model_dump(),
                    'tools': [tool.model_dump() for tool in result.tools]}

async def main():
    folder = Path.home()/'.config/nola-macm5/artcraft'
    manifest = json.loads((folder/'mcp.json').read_text())['mcpServers']
    outputs = {}
    for name, entry in manifest.items():
        try:
            outputs[name] = await asyncio.wait_for(inspect(name, entry), timeout=45)
            print(name, 'OK', len(outputs[name]['tools']), 'tools', flush=True)
        except Exception as error:
            outputs[name] = {'error': str(error)}
            print(name, 'FAILED', str(error), flush=True)
    (folder/'tools.json').write_text(json.dumps(outputs, indent=2)+'\n')
    if any('error' in entry for entry in outputs.values()):
        raise SystemExit(1)

if __name__ == '__main__':
    asyncio.run(main())
