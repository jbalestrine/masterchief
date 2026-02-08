#!/usr/bin/env python3
import subprocess, csv, io, sys

def get_python_pids():
    try:
        p = subprocess.run('tasklist /FI "IMAGENAME eq python.exe" /FO CSV', shell=True, capture_output=True, text=True)
        out = p.stdout
        lines=[l for l in out.splitlines() if l.strip()]
        if len(lines)<=1:
            return []
        reader = csv.reader(io.StringIO('\n'.join(lines)))
        next(reader)
        pids=[]
        for row in reader:
            if len(row)>=2:
                pid = row[1].strip('"')
                pids.append(pid)
        return pids
    except Exception:
        return []

def kill_pids(pids):
    stopped=[]
    for pid in pids:
        try:
            subprocess.run(['taskkill','/PID',pid,'/F'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stopped.append(pid)
        except Exception as e:
            print('Failed to stop', pid, e)
    return stopped

if __name__=='__main__':
    pids = get_python_pids()
    if not pids:
        print('No python processes found')
        sys.exit(0)
    print('Found python PIDs:', pids)
    stopped=kill_pids(pids)
    print('Stopped:', stopped)
    remaining = get_python_pids()
    print('Remaining python PIDs:', remaining)
