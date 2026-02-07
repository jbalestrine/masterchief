import socket
import time
import sys

out_file = r"tools/irc_client_out.txt"


def main():
    with open(out_file, 'w', encoding='utf-8') as f:
        def log(s):
            f.write(s + '\n'); f.flush()
        try:
            s = socket.socket()
            s.connect(('127.0.0.1', 6667))
            s.settimeout(1.0)
            s.sendall(b'NICK realtest\r\n')
            s.sendall(b'USER realtest 0 * :realtest\r\n')
            # read until 001
            buf = b''
            start = time.time()
            while time.time() - start < 10:
                try:
                    d = s.recv(4096)
                except Exception:
                    d = b''
                if not d:
                    time.sleep(0.1); continue
                buf += d
                txt = buf.decode(errors='replace')
                log('RECV: ' + txt)
                if ' 001 ' in txt:
                    break
            # join
            s.sendall(b'JOIN #masterchief\r\n')
            log('JOINED #masterchief, listening for 15s')
            end = time.time() + 15
            while time.time() < end:
                try:
                    d = s.recv(4096)
                except Exception:
                    time.sleep(0.1); continue
                if not d:
                    time.sleep(0.1); continue
                txt = d.decode(errors='replace')
                log('LINE: ' + txt.strip())
        except Exception as e:
            with open(out_file, 'a', encoding='utf-8') as ff:
                ff.write('ERROR: ' + str(e) + '\n')
        finally:
            try:
                s.close()
            except:
                pass


if __name__ == '__main__':
    main()
