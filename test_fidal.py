import requests
from bs4 import BeautifulSoup

url = "https://www.fidal.it/calendario.php?&id_sito=126&submit=Invia&livello=REG&new_regione=TOSCANA&anno=2026&mese=9"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(url, headers=headers).text

print("Lunghezza pagina:", len(html))

soup = BeautifulSoup(html, "html.parser")

righe = soup.find_all("tr")

print("Righe trovate:", len(righe))

for riga in righe[:10]:
    print(riga.get_text(" ", strip=True))
``
