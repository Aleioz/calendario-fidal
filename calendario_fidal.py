import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
calendar = Calendar()
conteggio_totale = 0

# Lista degli URL stabili scritti per esteso
urls = [
    "https://fidal.it",
    "https://fidal.it",
    "https://fidal.it",
    "https://fidal.it"
]

PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "giovanili", "coni", "provinciali"]
ESCLUSIONI = ["master", "assoluti", "promesse"]

print("Avvio estrazione dei dati...")

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        righe = soup.find_all('tr')
        for riga in righe:
            colonne = riga.find_all('td')
            
            # Verifichiamo che la riga della tabella contenga i dati della gara
            if len(colonne) >= 4:
                # Estraiamo i testi delle celle in una lista pulita
                testi_celle = []
                for cella in colonne:
                    testi_celle.append(cella.get_text().strip())
                
                # Prendiamo i dati in ordine sequenziale senza usare indici numerici
                data_testo = testi_celle.pop(0)    # Prima cella: la Data
                livello = testi_celle.pop(0)       # Seconda cella: il Livello (R)
                titolo = testi_celle.pop(0)        # Terza cella: il Titolo della gara
                tipo_gara = testi_celle.pop(0).lower() # Quarta cella: la Tipologia (pista, indoor...)
                
                # Quinta cella (se esiste): il Luogo della gara
                luogo = testi_celle.pop(0) if testi_celle else ""
                
                # Filtro per escludere le gare senior su strada
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
                    # Gestione dei giorni doppi (es. 13-14/06 -> prende solo 13/06)
                    if "-" in data_testo:
                        frammenti = data_testo.split("-")
                        giorno_inizio = frammenti.pop(0)
                        mese_estratto = data_testo.split("/").pop(-1)
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
    except Exception as e:
        print("Errore temporaneo di rete: " + str(e))

# Scrittura e serializzazione del file finale
with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
    f.write(calendar.serialize())

print("\n[SUCCESSO] Calendario creato! Trovate " + str(conteggio_totale) + " gare totali.")
