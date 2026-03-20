# setup.ps1
# --------------------------
# Dev environment setup for MasterChief app
# --------------------------

# --- Variables ---
$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvDir = Join-Path $repoDir "venv"
$modelsDir = Join-Path $repoDir "models"
$ggufFile = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
$ggufUrl = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf?download=true"

# --- Step 1: Ensure models folder exists ---
if (!(Test-Path $modelsDir)) {
    Write-Host "Creating models directory..."
    New-Item -ItemType Directory -Path $modelsDir | Out-Null
}

# --- Step 2: Download GGUF model if missing or incomplete ---
$ggufPath = Join-Path $modelsDir $ggufFile
$downloadGGUF = $false
if (!(Test-Path $ggufPath)) {
    $downloadGGUF = $true
} else {
    $size = (Get-Item $ggufPath).Length
    if ($size -lt 10000000) {  # 10 MB
        Write-Host "Existing GGUF file is too small, re-downloading..."
        Remove-Item $ggufPath
        $downloadGGUF = $true
    }
}

if ($downloadGGUF) {
    Write-Host "Downloading GGUF model..."
    try {
        Invoke-WebRequest -Uri $ggufUrl -OutFile $ggufPath -ErrorAction Stop
        Write-Host "GGUF model downloaded to $ggufPath"
    }
    catch {
        Write-Error "Failed to download GGUF model. Please check your internet connection or manually download it from:"
        Write-Host $ggufUrl
        exit 1
    }
} else {
    Write-Host "GGUF model already exists and looks good."
}

# --- Step 3: Setup virtual environment ---
if (!(Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvDir
}

# --- Step 4: Activate virtual environment ---
Write-Host "Activating virtual environment..."
& "$venvDir\Scripts\Activate.ps1"

# --- Step 5: Load .env if it exists ---
$envFile = Join-Path $repoDir ".env"
if (Test-Path $envFile) {
    Write-Host "Loading .env variables..."
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

# --- Step 6: Install Python requirements ---
Write-Host "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$repoDir\requirements.txt"

# --- Step 6b: Detect GPU availability ---
Write-Host "Detecting GPU availability..."
$gpuCheckScript = @"
import torch, os
if torch.cuda.is_available():
    os.environ['MC_USE_GPU'] = '1'
    print('GPU detected. Using GPU for inference.')
else:
    os.environ['MC_USE_GPU'] = '0'
    print('No GPU detected. Using CPU for inference.')
"@
python -c $gpuCheckScript

# --- Step 7: Start the app ---
Write-Host "Starting MasterChief app..."
python "$repoDir\main.py"