Write-Output "Running preload.ps1"

# Function to check if Ollama is installed
function Check-OllamaInstalled {
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        Write-Output "Ollama is already installed"
        return $true
    } else {
        Write-Output "Ollama is not installed"
        return $false
    }
}

# Function to check if phi3 is installed
function Check-LlavaInstalled {
    $llavaVersion = ollama list | Select-String "phi3"
    if ($llavaVersion) {
        Write-Output "phi3 is already installed"
        return $true
    } else {
        Write-Output "phi3 is not installed"
        return $false
    }
}

# Function to install Ollama on Windows
function Install-OllamaWindows {
    Invoke-WebRequest -Uri https://ollama.com/download/ollama-windows-amd64.exe -OutFile "C:\Windows\System32\ollama.exe"
}

# Function to add Ollama as a startup service on Windows
function Setup-ServiceWindows {
    New-Service -Name "Ollama" -Binary "C:\Windows\System32\ollama.exe serve" -Description "Ollama Service" -StartupType Automatic
    Start-Service -Name "Ollama"
}

# Main script
if (-not (Check-OllamaInstalled)) {
    Install-OllamaWindows
    Setup-ServiceWindows
}

if (-not (Check-LlavaInstalled)) {
    ollama pull phi3
}