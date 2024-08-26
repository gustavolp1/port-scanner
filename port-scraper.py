import requests
from bs4 import BeautifulSoup
import re
import json

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
                        
                        print(port_range, cleaned_text)

                        port_service_map[int(port_range)] = cleaned_text
                except:
                    continue

    return port_service_map

if __name__ == "__main__":
    port_service_map = port_scrape()

    for port, service in list(port_service_map.items())[:20]: 
        print(f"Port {port}: {service}")
    
    with open("scraped_ports.json", "w") as f:
        json.dump(port_service_map, f)