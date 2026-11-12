# WanGP (Windows, RTX 20XX–50XX) — instalação medida na Dell Precision 5860 (06/11/2026)

Pré-requisitos: driver NVIDIA R580+, git, uv. Alvo: `D:\WanGP`.

```powershell
git clone --depth 1 https://github.com/deepbeepmeep/Wan2GP.git D:\WanGP
cd D:\WanGP
uv venv --python 3.11 env_uv
$py = "D:\WanGP\env_uv\Scripts\python.exe"
uv pip install --python $py torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu130
uv pip install --python $py -r requirements.txt
uv pip install --python $py https://github.com/deepbeepmeep/WGPKernels/releases/download/v1.4.2/wgpkernels-1.4.2%2Bcu130-py3-none-win_amd64.whl
uv pip install --python $py -U "triton-windows>=3.7.0.post26,<=3.7.1.post27"
uv pip install --python $py "https://github.com/woct0rdho/SageAttention/releases/download/v2.2.0-windows.post6/sageattention-2.2.0+cu130torch2.10.0andhigher.post6-cp310-abi3-win_amd64.whl"
uv pip install --python $py https://github.com/deepbeepmeep/kernels/releases/download/Flash2/flash_attn-2.8.3-cp311-cp311-win_amd64.whl
uv pip install --python $py "https://github.com/woct0rdho/SpargeAttn/releases/download/v0.1.0-windows.post4/spas_sage_attn-0.1.0%2Bcu130torch2.9.0andhigher.post4-cp39-abi3-win_amd64.whl"
```

Copie `iniciar-wangp.bat` e `liberar-gpu.ps1` para `D:\WanGP`. UI em http://localhost:7860.

## Atenção
- `liberar-gpu.ps1` **encerra à força** modelos Ollama, IPED (java "iped") e Cellebrite/UFED antes de subir o WanGP (decisão do usuário). Pode interromper trabalho em curso. `-DryRun` só lista.
- Evitar PyTorch 2.8/2.9. Modelos baixam sob demanda (GB cada).
