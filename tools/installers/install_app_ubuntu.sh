#!/usr/bin/env bash
set -euo pipefail

APPNAME=""
APT_PKG=""
TAR_URL=""
INSTALL_DIR=""

usage(){
  echo "Usage: $0 --app <name> [--apt <pkg>] [--tar <url>] [--install-dir <dir>]"
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app) APPNAME="$2"; shift 2;;
    --apt) APT_PKG="$2"; shift 2;;
    --tar) TAR_URL="$2"; shift 2;;
    --install-dir) INSTALL_DIR="$2"; shift 2;;
    -h|--help) usage;;
    *) echo "Unknown arg: $1"; usage;;
  esac
done

if [[ -z "$APPNAME" ]]; then usage; fi

ROOT_DIR=$(dirname "$(dirname "$(realpath "$0")")")
STATUS_DIR="$ROOT_DIR/data/install_status"
mkdir -p "$STATUS_DIR"
STATUS_FILE="$STATUS_DIR/$APPNAME.json"

write_status(){
  python - <<PY -- "$STATUS_FILE" "$@"
import json,sys
path=sys.argv[1]
obj={}
for i,arg in enumerate(sys.argv[2:],start=2):
    # expects key=value pairs
    if '=' in arg:
        k,v=arg.split('=',1)
        obj[k]=v
print(json.dumps(obj))
PY
}

echo '{"app":"'$APPNAME'","state":"starting","started_at":"'$(date --iso-8601=seconds)'"}' > "$STATUS_FILE"

if [[ -n "$APT_PKG" ]]; then
  sudo apt-get update
  sudo apt-get install -y "$APT_PKG"
  echo '{"app":"'$APPNAME'","state":"installed","method":"apt","installed_at":"'$(date --iso-8601=seconds)'"}' > "$STATUS_FILE"
  exit 0
fi

if [[ -n "$TAR_URL" ]]; then
  if [[ -z "$INSTALL_DIR" ]]; then
    INSTALL_DIR="/opt/$APPNAME"
  fi
  sudo mkdir -p "$INSTALL_DIR"
  tmp=$(mktemp -u)/$APPNAME.tar.gz
  curl -L "$TAR_URL" -o "$tmp"
  sudo tar -xzf "$tmp" -C "$INSTALL_DIR"
  rm -f "$tmp"
  echo '{"app":"'$APPNAME'","state":"installed","method":"tar","install_dir":"'$INSTALL_DIR'","installed_at":"'$(date --iso-8601=seconds)'"}' > "$STATUS_FILE"
  exit 0
fi

echo '{"app":"'$APPNAME'","state":"skipped","reason":"no_install_method_provided"}' > "$STATUS_FILE"
exit 2
