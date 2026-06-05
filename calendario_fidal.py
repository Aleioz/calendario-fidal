import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

ANNO = "2026"
# URL ufficiale con tutti i mesi inseriti dell'anno corrente
url = "https://www.fidal.it/calendario.php?&id_sito=126&submit=Invia&livello=REG&new_regione=TOSCANA&anno=99&mese=99"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    print("Connessione al server FIDAL Toscana...")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    calendar = Calendar()
    
    # Parole chiave usate nei titoli del comitato Toscana
    PAROLE_GIOVANILI = ["ragazzi", "ragazze", "cadetti", "cadette", "esordienti", "eso", "allievi", "allieve", "juniores", "u20", "u16", "u14", "coni"]
    
    righe = soup.find_all('tr')
    conteggio_totale = 0
    
    for riga in righe:
        testo_riga = riga.get_text(" | ", strip=True)
        # Una riga valida del calendario ha la data all'inizio (es. 16/06 o 20-21/06)
        if "|" in testo_riga and ("/" in testo_riga.split("|")[0] or "-" in testo_riga.split("|")[0]):
            parti = [p.strip() for p in testo_riga.split("|")]
            
            if len(parti) >= 3:
                data_grezza = parti[0] # Es: "16/06" o "20-21/06"
                tipo_livello = parti[1] # Es: "R" o "P"
                titolo = parti[2] # Es: "TROFEO CONI 2026..."
                
                # Estrai tipo (PISTA, INDOOR, STRADA) e luogo se presenti nelle parti successive
                tipo_gara = ""
                luogo = ""
                for parte in parti[3:]:
                    if parte.upper() in ["PISTA", "INDOOR", "STRADA", "CROSS", "TRAIL"]:
                        tipo_gara = parte.upper()
                    elif "(" in parte and ")" in parte:
                        luogo = parte

                # Applica i filtri richiesti (Tieni PISTA/INDOOR, scarta STRADA/TRAIL puri se non giovanili)
                titolo_lower = titolo.lower()
                is_giovanile = any(cat in titolo_lower for cat in PAROLE_GIOVANILI)
                
                # Se è una gara su PISTA o INDOOR, o se c'è scritto esplicitamente che è giovanile
                if (tipo_gara in ["PISTA", "INDOOR"]) or is_giovanile:
                    
                    # Pulizia data per eventi singoli o di due giorni (es: "20-21/06" prende il 20)
                    try:
                        giorno_mese = data_grezza
                        if "-" in giorno_mese:
                            giorno_inizio = giorno_mese.split("-")[0]
                            mese = giorno_mese.split("/")[-1]
                            # Se il trattino è prima della barra (es. 20-21/06)
                            if "/" in giorno_mese.split("-")[1]:
                                giorno_mese = f"{giorno_inizio}/{mese}"
                        
                        data_pulita = f"{giorno_mese}/{ANNO}"
                        data_evento = datetime.strptime(data_pulita, "%d/%m/%Y")
                        
                        # Crea l'evento nel calendario
                        event = Event()
                        event.name = f"[{tipo_gara if tipo_gara else 'GARA'}] {titolo}"
                        event.begin = data_evento
                        if luogo:
                            event.location = luogo
                        event.make_all_day()
                        
                        calendar.events.add(event)
                        conteggio_totale += 1
                    except:
                        continue

    # Salva il file sul desktop
    with open('calendario_toscana.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar)
        
    print(f"\n[SUCCESSO] Il file 'calendario_toscana.ics' è pronto sul tuo Desktop!")
    print(f"Gare giovanili e su pista/indoor salvate con successo: {conteggio_totale}")

except Exception as e:
    print(f"Errore durante l'esecuzione dello script: {e}")

