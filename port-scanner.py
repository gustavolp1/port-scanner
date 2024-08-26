import requests
from bs4 import BeautifulSoup
import re
import json
import socket
import multiprocessing


def port_scrape():
    url = "https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    port_service_map = {}

    tables = soup.find_all("table", {"class": "wikitable"})

    for table in tables[1:3]:
        table_rows = table.find_all("tr")

        for row in table_rows[1:]:
            table_columns = row.find_all("td")

            if len(table_columns) >= 2:
                try:
                    if "Yes" in table_columns[1].text:
                        port_range = table_columns[0].text.strip()
                        service_name = table_columns[-1].text.strip()

                        cleaned_text = re.sub(r'\[.*?\]', '', service_name)

                        port_service_map[int(port_range)] = cleaned_text
                except:
                    continue

    return port_service_map


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


def main():
    while True:
        print("\nPython Port Scanner")
        
        target = input("Enter target IP or hostname: ")

        try:
            target = socket.gethostbyname(target)
        except socket.gaierror:
            print("\nERROR: Invalid host name.")
            continue
        
        print("\nScanning Target: " + target)
        
        port_range_input = input("\nEnter port range (start_port-end_port) or leave blank for common ports: ")
        
        if port_range_input:
            try:
                start_port, end_port = map(int, port_range_input.split('-'))
            except ValueError:
                print("\nERROR: Invalid port range.")
                continue
        else:
            start_port = None
            end_port = None

        print("\nScanning ports...")
        
        with multiprocessing.Manager() as manager:
            closed_ports = manager.list()
            processes_count = multiprocessing.cpu_count()
            pool = multiprocessing.Pool(processes=processes_count)

            if start_port is None:
                for port in MAIN_PORTS:
                    pool.apply_async(scan_port, args=(target, int(port), closed_ports))
            else:
                for port in range(start_port, end_port + 1):
                    pool.apply_async(scan_port, args=(target, port, closed_ports))

            pool.close()
            pool.join()

            if closed_ports:
                print("\nClosed Ports:")
                print(", ".join(str(port) for port in closed_ports))
            else:
                print("\nNo closed ports found.")

        repeat = input("\nDo you want to perform another scan? (yes/no): ").strip().lower()
        if repeat != 'yes':
            break


if __name__ == "__main__":
    print("\nScraping ports...")
    MAIN_PORTS = port_scrape()

    with open("scraped_ports.json", "w") as f:
        json.dump(MAIN_PORTS, f)

    main()
