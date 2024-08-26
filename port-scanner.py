import sys
import socket
import multiprocessing
import json

def main():

    print("\nPython Port Scanner")

    if len(sys.argv) > 4 or len(sys.argv) < 2:
        print("\nUsage: python3 scan.py <ip> <start_port> <end_port>")
        sys.exit()
    
    target = sys.argv[1]

    if not target.isnumeric():
        try:
            target = socket.gethostbyname(target)    
        except socket.gaierror:
            print("\nERROR: Invalid host name.")
            sys.exit()
    
    print("\nScanning Target: " + target)
    
    if len(sys.argv) == 2:
        start_port = None
        end_port = None
    else:
        start_port = int(sys.argv[2])
        end_port = int(sys.argv[3])

    with multiprocessing.Manager() as manager:
        closed_ports = manager.list()
        
        processes_count = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=processes_count)

        if start_port is None:
            for port in MAIN_PORTS:
                pool.apply_async(scan_port, args=(target, int(port), closed_ports))
        else:
            for port in range(start_port, end_port+1):
                pool.apply_async(scan_port, args=(target, port, closed_ports))

        pool.close()
        pool.join()

        if closed_ports:
            print("\nClosed Ports:")
            print(", ".join(str(port) for port in closed_ports))
        else:
            print("\nNo closed ports found.")

def read_ports():
    with open("scraped_ports.json", "r") as f:
        return json.load(f)

def scan_port(target, port, closed_ports):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((target, port))
        if result == 0:
            service = MAIN_PORTS.get(str(port), "Unknown Service")
            print(f"Port {port} is open. Service: {service}")
        else:
            closed_ports.append(port)
        s.close()
    except socket.timeout:
        print(f"Timeout occurred for port: {port}")
    except socket.error:
        print(f"\n Server not responding for port: {port}")
    finally:
        s.close()

if __name__ == "__main__":
    MAIN_PORTS = read_ports()
    main()