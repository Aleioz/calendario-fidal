import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
calendar = Calendar()
conteggio_totale = 0

# Controlliamo singolarmente i mesi stabili (6=Giugno, 7=Luglio, 9=Settembre, 10=Ottobre)
mesi_da_controllare = ["6", "7", "9", "10"]

PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "giovanili", "coni", "provinciali"]
ESCLUSIONI = ["master", "assoluti", "promesse"]

print("Avvio estrazione mensile dal database FIDAL Toscana...")

for m in mesi_da_controllare:
    # URL scritti in modo fisso e lineare senza variabili nascoste
    url = "https://fidal.it" + m
    print("Lettura mese numero: " + m)
    
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
                    if "-" in data_testo:
                        giorno_inizio = data_testo.split("-")[0]
                        mese_estratto = data_testo.split("/")[-1]
                        data_pulita = giorno_inizio + "/" + mese_estratto + "/2026"
                    else:
                        data_pulita = data_testo + "/2026"
                        
                    data_evento = datetime.strptime(data_pulita, "%d/%m/%Y")
                    
                    event = Event()
                    event.name = "[" + tipo_gara.upper() + "] " + titolo
                    event.begin = data_evento
                    if luogo:
                        event.location = luogo
                    event.make_all_day()
                    
                    calendar.events.add(event)
                    conteggio_totale += 1
                except:
                    continue
        time.sleep(0.5)
    except Exception as e:
        print("Errore rete: " + str(e))

with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
    f.write(calendar.serialize())

print("\n[SUCCESSO] Calendario creato! Trovate " + str(conteggio_totale) + " gari totali.")
