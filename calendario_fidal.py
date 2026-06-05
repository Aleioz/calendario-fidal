import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

ANNO = "2026"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
calendar = Calendar()
conteggio_totale = 0

# Controlliamo i mesi chiave in cui si concentrano le gare: Giugno (6), Luglio (7), Settembre (9), Ottobre (10)
mesi_da_controllare = [6, 7, 9, 10]

PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "giovanili"]
ESCLUSIONI = ["master", "assoluti", "promesse"]

print("Avvio scansione stagionale del calendario...")

for mese in mesi_da_controllare:
    # Genera l'URL mirato per il singolo mese sul database FIDAL Toscana (id_sito=126)
    url = f"https://www.fidal.it/calendario.php?&id_sito=126&submit=Invia&livello=REG&new_regione=TOSCANA&anno={ANNO}&mese={mese}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        righe = soup.find_all('tr')
        for riga in righe:
            colonne = riga.find_all('td')
            if len(colonne) >= 4:
                data_testo = colonne[0].text.strip()
                titolo = colonne[2].text.strip()
                tipo_gara = colonne[3].text.strip().lower()
                luogo = colonne[4].text.strip() if len(colonne) > 4 else ""
                
                # Salta le gare podistiche senior su strada
                if "strada" in tipo_gara or "trail" in tipo_gara or "montagna" in tipo_gara:
                    continue 
                    
                titolo_lower = titolo.lower()
                contiene_giovanili = any(cat in titolo_lower for cat in PAROLE_GIOVANILI)
                contiene_esclusioni = any(esc in titolo_lower for esc in ESCLUSIONI)
                
                if contiene_esclusioni and not contiene_giovanili:
                    continue
                    
                if not data_testo or "/" not in data_testo:
                    continue
                    
                try:
                    # Gestione dei giorni doppi (es. 13-14/06 -> prende il 13/06)
                    if "-" in data_testo:
                        giorno_inizio = data_testo.split("-")[0]
                        mese_estratto = data_testo.split("/")[-1]
                        data_pulita = f"{giorno_inizio}/{mese_estratto}/{ANNO}"
                    else:
                        data_pulita = f"{data_testo}/{ANNO}"
                        
                    data_evento = datetime.strptime(data_pulita, "%d/%m/%Y")
                    
                    event = Event()
                    event.name = f"[{tipo_gara.upper()}] {titolo}"
                    event.begin = data_evento
                    event.location = luogo
                    event.make_all_day()
                    
                    calendar.events.add(event)
                    conteggio_totale += 1
                except:
                    continue
    except Exception as e:
        print(f"Errore durante la lettura del mese {mese}: {e}")

# Scrittura finale del file unico online
with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
    f.writelines(calendar)

print(f"\n[SUCCESSO] Calendario creato con successo! Trovate {conteggio_totale} gare totali.")
