# Sdílené nabíječky elektromobilů
## Volba tématu
Chtěl bych vytvořit systém, který by dovolil lidem sdílet své domovní nabíječky elektromobilů ostatním podobně jako Airbnb sdílí obydlí.
## Analýza problému
### Nápad
Když jsem hledal, jestli něco takového existuje, zjistil jsem, že v Česku pravděpodobně pár pokusů bylo, ale stránky již nefungují. V zahraničí už některé projekty existují, například:
- [Go Plugable](https://www.goplugable.com/)
- [Plug Inn](https://www.pluginn.app/en/)
Go Plugable ale nabízí kompletní stanice. Tomu bych se chtěl vyhnout a chtěl bych využívat nabíjecí stanice, které už uživatel doma vlastní. Uživatelé si tedy nebudou muset kupovat novou nabíjecí stanici za desítky tisíc korun, ale můžou využít současnou nabíječku.
### Inspirace
- [https://chargemyhyundai.com](https://chargemyhyundai.com)
- [https://www.evmapa.cz/#](https://www.evmapa.cz/#)
## Výběr postupu a technologií
### Síťová komunikace
Chci využít **OCPP 1.6 JSON přes WebSocket** jako hlavní protokol pro komunikaci mezi nabíječkami a backendem. Nabíječky (např. Solax X3-HAC) budou OCPP klienty a připojí se přímo na OCPP server běžící v cloudu.  
OCPP server bude implementovaný v **Node.js**, které je vhodné pro stovky až tisíce dlouhodobě otevřených spojení.
### Autentizace
Autentizace proběhne pomocí **RFID čtečky zabudované přímo v nabíječce**.  
Nabíječka po přečtení RFID odešle ID karty na backend přes OCPP zprávu `Authorize`. Backend ověří platnost karty a odpoví nabíječce.  
Použití ESP32 nebo Raspberry Pi Pico se zvažuje pouze pro nabíječky, které nemají vlastní RFID čtečku a/nebo OCPP podporu. V tom případě bude ESP32 fungovat jako prostředník (REST klient a řídicí jednotka).
### Platby
Po ukončení nabíjení backend vypočítá částku a provede automatické stržení kreditu uživatele, případně odečte přímo z účtu. Pro integraci plateb zvažuji využití kreditního systému nebo **GoPay API**.
## Backend a API
- **Node.js**: OCPP WebSocket server pro komunikaci s nabíječkami.  
- **FastAPI (Python)**: API server pro mobilní aplikaci a web (uživatelé, platby, historie, rezervace). Poskytuje také automaticky generovanou dokumentaci API.  
- **Redis**: cache, sessions, mapování websocket ID ↔ uživatel, real-time propojení mezi Node.js a FastAPI.  
### Databáze
Pro uložení uživatelů, historie nabíjení, dat o nabíječkách a autorizacích použiji **PostgreSQL** – stabilní a robustní relační databázi.  
### Webová aplikace
Frontend webu bude vyvíjen v **SvelteKit**, který umožňuje rychlý vývoj, má vestavěný routing a podporuje server-side rendering.  
Webová aplikace nabídne přístup k mapě nabíječek, historii nabíjení a správě uživatelských účtů.
### Mobilní aplikace
Pro mobilní aplikaci zvolím **Flutter**. Umožní psát jeden kód pro Android i iOS, s možností snadno zobrazovat mapu nabíječek, kredit, historii nabíjení i rezervace.
### Geolokace a mapa nabíječek
Zobrazování nabíječek na mapě bude realizováno pomocí **Leaflet.js** (web) a **Mapbox SDK** nebo Google Maps (mobilní aplikace Flutter).
### Bezpečnost
- API bude zabezpečeno pomocí **JWT tokenů**.  
- Veškerá komunikace poběží přes **HTTPS**.  
- Implementace uživatelských rolí (majitel, uživatel, admin).  
- Ochrana přes CORS, rate limiting a další bezpečnostní opatření.
## Stanovení cílů
1. Sprovoznit komunikaci s nabíječkami, které mají **integrovanou RFID čtečku a OCPP klienta** (např. Solax X3 HAC). Backend bude přijímat `Authorize` požadavky a řídit nabíjení přes OCPP.  
2. Vytvořit responzivní webovou aplikaci v **SvelteKit** s mapou nabíječek, správou uživatelských účtů, historií nabíjení a statistikami.  
3. Implementovat automatické strhávání plateb (kreditní systém nebo GoPay).  
4. Vyvinout mobilní aplikaci ve **Flutteru** se stejnými funkcemi jako web (mapa, kredit, historie, rezervace).  
### Volitelné cíle
- Podpora dalších značek nabíječek bez OCPP.  
- Statistiky o původu elektřiny (obnovitelné/neobnovitelné).  
## Časový rozvrh
Po celou dobu projektu si budu psát pracovní verzi dokumentace, kterou potom přetvořím do finální prezentace.  
### Září
- Vytvoření WebSocket serveru
- Zprovoznění komunikace WebSocket serveru s nabíjčkami a API
- Běh WebSocket serveru v dockeru
### Říjen
- Dokončení logiky WebSocket server při nabíjení (Autentizace, Start a Stop nabíjení)
- Vytvoření API serveru
- Přidání docker compose, aby vše běželo v dockeru
- Vytvoření přehledného dashboardu v SvelteKit.  
### Listopad
- Dokončení webu (přidání mapy, ....)
- Vyvinutí základní verze mobilní aplikace ve Flutteru.  
### Prosinec
- Příprava prezentace a dokumentace.
- Rezerva pro skluz nebo volitelné cíle.  
## Získání potřebných znalostí a dovedností
- Seznámím se s OCPP.  
- Zdokonalím se v Node.js (pro websocket server), Pythonu (FastAPI), databázích (PostgreSQL) a práci s Redisem.  
- Naučím se používat SvelteKit pro frontend a Flutter pro mobilní vývoj.  
