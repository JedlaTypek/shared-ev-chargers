# Sdílené nabíječky elektromobilů
## Volba tématu
Chtěl bych vytvořit systém, který by dovolil lidem sdílet své domovní nabíječky elektromobilů ostatním podobně jako Airbnb sdílí obydlí.
## Analýza problému
### Nápad
Když jsem hledal, jestli něco takového existuje, zjistil jsem, že v Česku pravděpodobně pár pokusů bylo, ale stránky již nefungují. V zahraničí už nějaké projekty existují, například:
- [Go Plugable](https://www.goplugable.com/)
- [Plug Inn](https://www.pluginn.app/en/)

Go Plugable ale nabízí kompletní stanice. Tomu bych se chtěl vyhnout a chtěl bych využívat nabíjecí stanice, které už uživatel doma vlastní. Uživatelé si tedy nebudou muset kupovat nabíjecí stanici za desítky tisíc korun ale můžou využít současnou nabíječku.
## Výběr postupu a technologií
### Síťová komunikace
Chci využít **OCPP 1.6 JSON přes WebSocket** jako hlavní protokol pro komunikaci mezi nabíječkami a backendem. Nabíječky (např. Solax X3-HAC) budou OCPP klienty a připojí se přímo na OCPP server v cloudu.
### Autentizace
Autentizace proběhne pomocí **RFID čtečky zabudované přímo v nabíječce**.  
Nabíječka po přečtení RFID odešle ID karty na backend přes OCPP zprávu `Authorize`. Backend ověří platnost karty a odpoví nabíječce.  
Použití ESP32 nebo Raspberry Pi Pico jako prostředníka se zvažuje pouze pro nabíječky, které nemají vlastní RFID čtečku a/nebo OCPP podporu. V tom případě bude ESP32 fungovat jako REST klient a řídící jednotka (ne OCPP server).
### Platby
Po ukončení nabíjení backend vypočítá částku a provede automatické stržení z účtu uživatele, případně odečte kredit. Pro integraci plateb zvažuji využití knihovny **gopay-sdk**, jejíž použitelnost ještě ověřím.
### Backend a API
Backend bude postavený na **Pythonu s FastAPI** pro jednoduchost, rychlou vývojovou iteraci a vestavěnou dokumentaci API. Jako OCPP server zvolím OpenOCPP.
### Databáze
Pro uložení uživatelů, historie nabíjení, dat o nabíječkách a autorizacích použiji **PostgreSQL** – stabilní a robustní relační databázi.
### Webová aplikace
Pro uživatelské rozhraní zvolím **Django** (může být i Django REST Framework pro API), které dobře ladí s PostgreSQL a usnadní správu uživatelů a rolí.
### Frontend framework
Pro frontend bude primárně použitý **Django templating**, s možností přidat **React** nebo jinou moderní JS knihovnu, pokud se rozsah projektu rozroste.
### Geolokace a mapa nabíječek
Zobrazování nabíječek na mapě bude realizováno pomocí **Leaflet.js**, případně s integrací Mapbox nebo Google Maps API, podle potřeb uživatelského rozhraní.
### Bezpečnost
- API bude zabezpečeno pomocí **JWT tokenů** nebo jiné tokenové autentizace.
- Veškerá komunikace poběží přes **HTTPS**.
- Implementace uživatelských rolí (majitel, uživatel, admin).
- Dodržení bezpečnostních praktik (CORS, CSRF, rate limiting apod.).
## Stanovení cílů
1. Sprovoznit komunikaci s nabíječkami, které mají **integrovanou RFID čtečku a OCPP klienta** (např. Solax X3 HAC). Backend bude přijímat `Authorize` požadavky a řídit nabíjení přes OCPP.
2. Vytvořit responzivní webovou aplikaci s mapou nabíječek, správou uživatelských účtů, historií nabíjení a statistikami. 
3. Implementovat automatické strhávání plateb (online platby nebo odečet z kreditu).
4. Rezervační systém nabíječek.
### Volitelné cíle
- Podpora dalších značek nabíječek bez OCPP
- Statistiky o původu elektřiny (obnovitelné/neobnovitelné)
- Vývoj mobilní aplikace pro autentizaci přes NFC a správu nabíjení.
## Časový rozvrh
Po celou dobu projektu si budu psát pracovní verzi dokumentace, kterou potom přetvořím do publikování-schopné verze.
### Srpen
- Seznámení s OCPP
- Vývoj vlastního backendu a API serveru.
- Sprovoznění autentizace a start/stop nabíjení
### Září
- Odesílání údajů o nabíjení (ID stanice, ID uživatele, kWh, čas začátku a konce).
- Zprovoznění platební logiky (GoPay nebo kreditní systém).
### Říjen
- Vytvoření přehledné dashboardy uživatelů se statistikami
- Vytvoření mapy s nabíječkami
### Listopad
- Rezerva pro skluz nebo volitelné cíle.
- Úprava dokumentace
### Prosinec
- Příprava prezentace
## Získání potřebných znalostí a dovedností
- Seznámím se s OCPP.
- Zdokonalím se v Pythonu, tvorbě API (FastAPI), databází (PostgreSQL) a v práci v Djangu.
- Zvážím vývoj mobilní aplikace (pokud zbyde čas na autentizaci přes NFC v mobilu).
