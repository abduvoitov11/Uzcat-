#!/usr/bin/env python3
import socket
import sys
import threading
import argparse
import os
import time

# Python 3.12+ tizimlarida buyruqlar tarixini qo'llab-quvvatlash
try:
    import readline
except ImportError:
    pass

# Terminal vizual ranglari uchun ANSI kodlari
YASHIL = "\033[92m"
KOK = "\033[94m"
QIZIL = "\033[91m"
SARIQ = "\033[93m"
TOQ_KOK = "\033[36m"
QALIN = "\033[1m"
RESET = "\033[0m"

# Katta vizual UZCAT banneri
BANNER = f"""{YASHIL}{QALIN}
  _    _ ______ _____          _______ 
 | |  | |___  // ____|   /\\   |__   __|
 | |  | |  / /| |       /  \\     | |   
 | |  | | / / | |      / /\\ \\    | |   
 | |__| |/ /__| |____ / ____ \\   | |   
  \\____//______\\_____/_/    \\_\\  |_|   v3.1 (Enterprise Open-Source)
{RESET}"""

# Ikki tilli lokalizatsiya matnlari paketi
LANG_PACK = {
    "uz": {
        "desc": "Netcat funksiyalari + Port Forwarding + Multi-Client + Port Knocking + TTL & History",
        "err_format": "Format noto'g'ri. Misol: 21-80",
        "scan_start": "Skaner ishlamoqda: {}",
        "port": "PORT", "status": "HOLAT", "service": "TIZIM XIZMATI", "open": "OCHIQ",
        "forward_active": "Port Forwarding faol: {}:{} -> {}:{}",
        "forward_req": "Yo'naltirish so'rovi qabul qilindi: {}:{}",
        "forward_err": "Maqsadli xostga bog'lanib bo'lmadi ({}:{}): {}",
        "udp_start": "UDP Tinglovchi ishga tushdi [{}:{}]...",
        "tcp_start": "TCP Tinglovchi faol [{}:{}]. Ulanishlar kutilmoqda...",
        "conn_success": "Ulanish amalga oshdi: {}:{}",
        "file_recv": "Fayl qabul qilinmoqda: {}",
        "file_ok": "Fayl muvaffaqiyatli qabul qilindi.",
        "remote_drop": "Masofaviy aloqa uzildi.",
        "knock_wait": "Port Knocking ketma-ketligi kutilmoqda: {}",
        "knock_success": "Port Knocking muvaffaqiyatli! Asosiy port ochilmoqda...",
        "knock_fail": "Port Knocking taymauti yakunlandi. Port ochilmadi.",
        "ttl_expired": "TTL (Dead Man's Switch) vaqti tugadi. Tizim xavfsiz yopilmoqda...",
        "reconnect_try": "Aloqa uzildi. Qayta ulanish urinishi {}/{}...",
        "multi_broadcast": "Xabar barcha faol mijozlarga ({}) yuborildi.",
        "sig_stop": "Jarayon foydalanuvchi tomonidan to'xtatildi.",
        # Help menyulari uchun lokalizatsiya matnlari
        "main_desc": "Uzcat Enterprise - Kali Linux uchun yuqori darajadagi tarmoq auditi va tahlili vositasi.",
        "lang_help": "Interfeys tilini tanlang (Standart: en)",
        "mode_help": "Ishga tushirish rejimlari",
        "listen_help": "Portni tinglash (Server Rejimi)",
        "connect_help": "Masofaviy xostga ulanish (Client Rejimi)",
        "scan_help": "Tezkor portlarni diagnostika qilish (Skaner Rejimi)",
        "forward_help": "Port Forwarding / Trafikni boshqa manzilga yo'naltirish",
        "arg_port": "Tinglanadigan / ulanadigan port raqami",
        "arg_host": "Tinglanadigan IP manzil (Standart: 0.0.0.0)",
        "arg_udp": "UDP rejimini faollashtirish",
        "arg_keep": "Mijoz uzilganda ham portni yopmaslik (Keep-Open)",
        "arg_hex": "Oqimdagi ma'lumotlarni HEX (Wireshark kabi) formatda ko'rish",
        "arg_file": "Oqim orqali fayl qabul qilish / yuborish",
        "arg_knock": "Port Knocking xavfsizlik ketma-ketligini yoqish, misol: '1000,2000,3000'",
        "arg_ttl": "Avtomatik o'chish uchun hayot davri (TTL) soniyalarda",
        "arg_target": "Maqsadli IP yoki Domen manzili",
        "arg_reconnect": "Ulanish uzilganda qayta ulanish urinishlari soni",
        "arg_ports": "Skaner qilinadigan portlar, misol: 22-80 yoki 80,443",
        "arg_lport": "Tizimda ochiladigan lokal port raqami",
        "arg_rtarget": "Trafik yo'naltiruvchi masofaviy xost IP manzili",
        "arg_rport": "Masofaviy xost port raqami",
        "arg_lhost": "Lokal IP manzil (Standart: 0.0.0.0)"
    },
    "en": {
        "desc": "Netcat features + Port Forwarding + Multi-Client + Port Knocking + TTL & History",
        "err_format": "Invalid format. Example: 21-80",
        "scan_start": "Scanner running: {}",
        "port": "PORT", "status": "STATUS", "service": "SERVICE", "open": "OPEN",
        "forward_active": "Port Forwarding active: {}:{} -> {}:{}",
        "forward_req": "Forward request accepted: {}:{}",
        "forward_err": "Could not connect to remote host ({}:{}): {}",
        "udp_start": "UDP Listener started [{}:{}]...",
        "tcp_start": "TCP Listener active [{}:{}]. Waiting for connections...",
        "conn_success": "Connection established: {}:{}",
        "file_recv": "Receiving file: {}",
        "file_ok": "File received successfully.",
        "remote_drop": "Remote connection closed.",
        "knock_wait": "Waiting for Port Knocking sequence: {}",
        "knock_success": "Port Knocking sequence successful! Opening main port...",
        "knock_fail": "Port Knocking timeout reached. Port locked.",
        "ttl_expired": "TTL (Dead Man's Switch) expired. Securely shutting down...",
        "reconnect_try": "Connection lost. Reconnecting attempt {}/{}...",
        "multi_broadcast": "Message broadcasted to all active clients ({}).",
        "sig_stop": "Process interrupted by user.",
        # Help menu texts
        "main_desc": "Uzcat Enterprise - Advanced Network Audit and Analysis Utility for Kali Linux.",
        "lang_help": "Select Interface Language (Default: en)",
        "mode_help": "Execution Modes",
        "listen_help": "Listen on a port (Server Mode)",
        "connect_help": "Connect to a remote host (Client Mode)",
        "scan_help": "Fast Port Diagnosis (Scanner Mode)",
        "forward_help": "Port Forwarding / Relay Tunneling",
        "arg_port": "Port number to listen/connect",
        "arg_host": "Host IP to bind (Default: 0.0.0.0)",
        "arg_udp": "Enable UDP stream mode",
        "arg_keep": "Keep server open after client disconnection",
        "arg_hex": "Analyze incoming/outgoing traffic in HEX dump format",
        "arg_file": "Send or receive a file over the stream",
        "arg_knock": "Enable Port Knocking sequence, e.g., '1000,2000,3000'",
        "arg_ttl": "Time-To-Live in seconds for automatic safe shutdown",
        "arg_target": "Target IP or Domain address",
        "arg_reconnect": "Number of auto-reconnection attempts if disconnected",
        "arg_ports": "Ports to scan, e.g., 22-80 or 80,443",
        "arg_lport": "Local port to open on the system",
        "arg_rtarget": "Remote target IP to relay traffic",
        "arg_rport": "Remote port on target host",
        "arg_lhost": "Local host IP to bind (Default: 0.0.0.0)"
    }
}

# Global til sozlamasi
CURRENT_LANG = "en"
def msg(key): return LANG_PACK[CURRENT_LANG].get(key, "")

def log_info(text): print(f"{KOK}[*]{RESET} {text}")
def log_success(text): print(f"{YASHIL}[+]{RESET} {text}")
def log_error(text): print(f"{QIZIL}[-]{RESET} {text}")
def log_warning(text): print(f"{SARIQ}[!]{RESET} {text}")

# Global faol mijozlar ro'yxati (Asinxron Multi-Client boshqaruvi uchun)
active_clients = []
clients_lock = threading.Lock()

def format_hex_dump(data):
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"{TOQ_KOK}{i:04x}{RESET}  {hex_part:<47}  {YASHIL}|{ascii_part}|{RESET}")
    return "\n".join(lines)

def start_ttl_timer(seconds):
    def timeout_trigger():
        time.sleep(seconds)
        print(f"\n{QIZIL}{msg('ttl_expired')}{RESET}")
        os._exit(0)
    threading.Thread(target=timeout_trigger, daemon=True).start()

def wait_for_knocking(knock_str, host="0.0.0.0"):
    try:
        ports = [int(p) for p in knock_str.split(",")]
    except ValueError:
        return False
    
    log_info(msg("knock_wait").format(ports))
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(15)
        try:
            s.bind((host, port))
            s.listen(1)
            conn, _ = s.accept()
            conn.close()
        except socket.timeout:
            log_error(msg("knock_fail"))
            return False
        finally:
            s.close()
    log_success(msg("knock_success"))
    return True

def handle_client_receive(sock, show_hex):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            if show_hex:
                print(f"\n{SARIQ}[HEX DATA - {len(data)} bytes]{RESET}")
                print(format_hex_dump(data))
            else:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
        except Exception:
            break
    
    with clients_lock:
        if sock in active_clients:
            active_clients.remove(sock)
    sock.close()

def start_stdin_broadcast(show_hex):
    def stdin_loop():
        while True:
            try:
                if sys.stdin.isatty():
                    line = input().encode('utf-8') + b'\n'
                else:
                    line = sys.stdin.buffer.readline()
                if not line:
                    break
                
                with clients_lock:
                    dead_clients = []
                    for client in active_clients:
                        try:
                            client.sendall(line)
                        except Exception:
                            dead_clients.append(client)
                    for dc in dead_clients:
                        if dc in active_clients:
                            active_clients.remove(dc)
            except (KeyboardInterrupt, EOFError):
                break
            except Exception:
                break
    threading.Thread(target=stdin_loop, daemon=True).start()

def run_server(host, port, use_udp, keep_open, show_hex, filename, knock, ttl):
    if ttl: start_ttl_timer(ttl)
    if knock and not wait_for_knocking(knock, host): return

    sock_type = socket.SOCK_DGRAM if use_udp else socket.SOCK_STREAM
    server = socket.socket(socket.AF_INET, sock_type)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        if use_udp:
            log_success(msg("udp_start").format(host, port))
            while True:
                data, addr = server.recvfrom(4096)
                if show_hex:
                    print(f"\n{SARIQ}[UDP - {addr[0]}:{addr[1]}]{RESET}")
                    print(format_hex_dump(data))
                else:
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
        else:
            server.listen(50)
            log_success(msg("tcp_start").format(host, port))
            start_stdin_broadcast(show_hex)
            
            while True:
                conn, addr = server.accept()
                log_success(msg("conn_success").format(addr[0], addr[1]))
                
                if filename:
                    log_info(msg("file_recv").format(filename))
                    with open(filename, 'wb') as f:
                        while chunk := conn.recv(4096):
                            f.write(chunk)
                    log_success(msg("file_ok"))
                    conn.close()
                    if not keep_open: break
                else:
                    with clients_lock:
                        active_clients.append(conn)
                    threading.Thread(target=handle_client_receive, args=(conn, show_hex), daemon=True).start()
                    if not keep_open and len(active_clients) == 1:
                        break
            
            if not keep_open:
                while active_clients: time.sleep(0.5)
    except Exception as e:
        log_error(f"Server Error: {e}")
    finally:
        server.close()

def run_client(host, port, use_udp, show_hex, filename, ttl, reconnect):
    if ttl: start_ttl_timer(ttl)
    attempts = reconnect if reconnect else 1
    
    for i in range(attempts):
        sock_type = socket.SOCK_DGRAM if use_udp else socket.SOCK_STREAM
        client = socket.socket(socket.AF_INET, sock_type)
        try:
            if not use_udp:
                client.settimeout(10)
                client.connect((host, port))
                client.settimeout(None)
                log_success(msg("conn_success").format(host, port))
                
                if filename:
                    if not os.path.exists(filename): return
                    with open(filename, 'rb') as f:
                        while chunk := f.read(4096): client.sendall(chunk)
                    client.close()
                    return
                
                with clients_lock: active_clients.append(client)
                start_stdin_broadcast(show_hex)
                handle_client_receive(client, show_hex)
                break
            else:
                log_success(f"UDP Stream targeted to {host}:{port}")
                with clients_lock: active_clients.append(client)
                def udp_send_loop():
                    while True:
                        line = sys.stdin.buffer.readline()
                        if not line: break
                        client.sendto(line, (host, port))
                threading.Thread(target=udp_send_loop, daemon=True).start()
                while True:
                    data, _ = client.recvfrom(4096)
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
        except Exception:
            if reconnect and i < attempts - 1:
                log_warning(msg("reconnect_try").format(i + 1, attempts))
                time.sleep(3)
            else:
                log_error(msg("remote_drop"))
                break

def pipe_sockets(src, dst):
    while True:
        try:
            data = src.recv(4096)
            if not data: break
            dst.sendall(data)
        except: break
    src.close()
    dst.close()

def run_forwarder(local_host, local_port, remote_host, remote_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((local_host, local_port))
        server.listen(50)
        log_success(msg("forward_active").format(local_host, local_port, remote_host, remote_port))
        while True:
            client_sock, addr = server.accept()
            log_info(msg("forward_req").format(addr[0], addr[1]))
            try:
                remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote_sock.connect((remote_host, remote_port))
                threading.Thread(target=pipe_sockets, args=(client_sock, remote_sock), daemon=True).start()
                threading.Thread(target=pipe_sockets, args=(remote_sock, client_sock), daemon=True).start()
            except Exception as e:
                log_error(msg("forward_err").format(remote_host, remote_port, e))
                client_sock.close()
    except Exception as e:
        log_error(f"Forwarder Error: {e}")
    finally:
        server.close()

def run_scanner(target, ports_str):
    log_info(msg("scan_start").format(target))
    try:
        if "-" in ports_str:
            start, end = map(int, ports_str.split("-"))
            ports = list(range(start, end + 1))
        else:
            ports = [int(p) for p in ports_str.split(",")]
    except ValueError:
        log_error(msg("err_format"))
        return

    print(f"\n{QALIN}{TOQ_KOK}{msg('port'):<10}{msg('status'):<10}{msg('service'):<20}{RESET}")
    print("-" * 45)
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        if s.connect_ex((target, port)) == 0:
            try: service = socket.getservbyport(port)
            except: service = "unknown"
            print(f"{YASHIL}{port:<10}{msg('open'):<10}{service:<20}{RESET}")
        s.close()
    print("-" * 45)

def main():
    global CURRENT_LANG
    
    # 1-BOSQICH: Tilni barcha buyruqlardan oldin o'qib olib global o'zgaruvchini o'rnatish
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--lang", choices=["uz", "en"], default="en")
    known_args, _ = pre_parser.parse_known_args()
    if known_args.lang:
        CURRENT_LANG = known_args.lang

    print(BANNER)

    # 2-BOSQICH: Asosiy menyu va sub-menyularni tanlangan til (CURRENT_LANG) asosida yaratish
    parser = argparse.ArgumentParser(
        description=msg("main_desc"),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--lang", choices=["uz", "en"], default=CURRENT_LANG, help=msg("lang_help"))
    
    subparsers = parser.add_subparsers(dest="mode", help=msg("mode_help"))

    # LISTEN SUB-COMMAND
    l_p = subparsers.add_parser("listen", help=msg("listen_help"))
    l_p.add_argument("-p", "--port", type=int, required=True, help=msg("arg_port"))
    l_p.add_argument("-s", "--host", default="0.0.0.0", help=msg("arg_host"))
    l_p.add_argument("-u", "--udp", action="store_true", help=msg("arg_udp"))
    l_p.add_argument("-k", "--keep", action="store_true", help=msg("arg_keep"))
    l_p.add_argument("--hex", action="store_true", help=msg("arg_hex"))
    l_p.add_argument("-f", "--file", help=msg("arg_file"))
    l_p.add_argument("--knock", help=msg("arg_knock"))
    l_p.add_argument("--ttl", type=int, help=msg("arg_ttl"))

    # CONNECT SUB-COMMAND
    c_p = subparsers.add_parser("connect", help=msg("connect_help"))
    c_p.add_argument("-t", "--target", required=True, help=msg("arg_target"))
    c_p.add_argument("-p", "--port", type=int, required=True, help=msg("arg_port"))
    c_p.add_argument("-u", "--udp", action="store_true", help=msg("arg_udp"))
    c_p.add_argument("--hex", action="store_true", help=msg("arg_hex"))
    c_p.add_argument("-f", "--file", help=msg("arg_file"))
    c_p.add_argument("--ttl", type=int, help=msg("arg_ttl"))
    c_p.add_argument("--reconnect", type=int, help=msg("arg_reconnect"))

    # SCAN SUB-COMMAND
    s_p = subparsers.add_parser("scan", help=msg("scan_help"))
    s_p.add_argument("-t", "--target", required=True, help=msg("arg_target"))
    s_p.add_argument("-p", "--ports", required=True, help=msg("arg_ports"))

    # FORWARD SUB-COMMAND
    f_p = subparsers.add_parser("forward", help=msg("forward_help"))
    f_p.add_argument("-l", "--local-port", type=int, required=True, help=msg("arg_lport"))
    f_p.add_argument("-t", "--remote-target", required=True, help=msg("arg_rtarget"))
    f_p.add_argument("-r", "--remote-port", type=int, required=True, help=msg("arg_rport"))
    f_p.add_argument("-s", "--local-host", default="0.0.0.0", help=msg("arg_lhost"))

    args = parser.parse_args()
    
    print(f"{KOK}{QALIN}  >> {msg('desc')}{RESET}\n")

    if args.mode == "listen":
        run_server(args.host, args.port, args.udp, args.keep, args.hex, args.file, args.knock, args.ttl)
    elif args.mode == "connect":
        run_client(args.target, args.port, args.udp, args.hex, args.file, args.ttl, args.reconnect)
    elif args.mode == "scan":
        run_scanner(args.target, args.ports)
    elif args.mode == "forward":
        run_forwarder(args.local_host, args.local_port, args.remote_target, args.remote_port)
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{SARIQ}[!] {msg('sig_stop')}{RESET}")
        sys.exit(0)
