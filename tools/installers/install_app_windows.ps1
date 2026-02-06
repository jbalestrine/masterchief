Param(
    [Parameter(Mandatory=$true)][string]$AppName,
    [string]$ChocoPackage = "",
    [string]$ZipUrl = "",
    [string]$InstallDir = ""
)

function Write-Status($path, $obj){
    $json = $obj | ConvertTo-Json -Depth 10
    $json | Out-File -FilePath $path -Encoding UTF8
}

$root = (Resolve-Path "$PSScriptRoot\..\..\")
$statusDir = Join-Path $root 'data\install_status'
if(-not (Test-Path $statusDir)) { New-Item -ItemType Directory -Path $statusDir | Out-Null }
$statusFile = Join-Path $statusDir "$AppName.json"

Write-Status $statusFile @{app=$AppName; state='starting'; started_at=(Get-Date).ToString('o')}

try{
    if($ChocoPackage -ne ""){
        Write-Output "Installing $ChocoPackage via Chocolatey..."
        choco install $ChocoPackage -y | Out-Null
        $rc = $LASTEXITCODE
        if($rc -eq 0){
            Write-Status $statusFile @{app=$AppName; state='installed'; method='choco'; installed_at=(Get-Date).ToString('o')}
            exit 0
        } else {
            Write-Status $statusFile @{app=$AppName; state='failed'; reason=('choco_exit_'+$rc)}
            exit $rc
        }
    }

    if($ZipUrl -ne ""){
        if($InstallDir -eq ""){
            $InstallDir = Join-Path $env:ProgramFiles $AppName
        }
        if(-not (Test-Path $InstallDir)) { New-Item -ItemType Directory -Path $InstallDir | Out-Null }
        $tmp = Join-Path $env:TEMP ("$AppName.zip")
        Invoke-WebRequest -Uri $ZipUrl -OutFile $tmp
        Expand-Archive -Path $tmp -DestinationPath $InstallDir -Force
        Remove-Item $tmp -Force
        Write-Status $statusFile @{app=$AppName; state='installed'; method='zip'; install_dir=$InstallDir; installed_at=(Get-Date).ToString('o')}
        exit 0
    }

    Write-Status $statusFile @{app=$AppName; state='skipped'; reason='no_install_method_provided'}
    exit 2
} catch {
    Write-Status $statusFile @{app=$AppName; state='failed'; error=$_.Exception.Message}
    exit 1
}
