# Remove __pycache__ directories and .pyc files, then run pytest
Get-ChildItem -Recurse -Directory -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -eq '__pycache__' } |
  ForEach-Object { Remove-Item -Recurse -Force $_.FullName -ErrorAction SilentlyContinue }
Get-ChildItem -Recurse -Force -Filter *.pyc -ErrorAction SilentlyContinue |
  ForEach-Object { Remove-Item -Force $_.FullName -ErrorAction SilentlyContinue }

# Run pytest with quiet output
pytest -q
