# Sdílené nabíječky elektromobilů

## Volba tématu
Chtěl bych vytvořit systém, který by dovolil lidem sdílet své domovní nabíječky elektromobilů ostatním podobně jako Airbnb sdílí obydlí.

## Analýza problému

### Nápad
Když jsem hledal, jestli něco takového existuje, zjistil jsem, že v Česku pravděpodobně pár pokusů bylo, ale stránky již nefungují. V zahraničí už nějaké projekty existují, například:
- [Go Plugable](https://www.goplugable.com/)
- [Plug Inn](https://www.pluginn.app/en/)

Go Plugable ale nabízí kompletní stanice. Tomu bych se chtěl vyhnout a chtěl bych využívat nabíjecí stanice, které už uživatel doma vlastní. Uživatelé si tedy nebudou muset kupovat nabíjecí stanici za desítky tisíc korun ale pouze krabičku (mezičlen) za pár stovek a zároveň se neošidí o prémiové funkce ekosysétmu jejich značky.

## Výběr postupu a technologií

### Autentizace
K autentizaci chci využít **ESP32** nebo **Raspberry Pi Pico**, které budou sloužit jako prostředník mezi serverem a nabíjecí stanicí. Pokud nabíječka nemá vlastní API, mezičlen bude tuto komunikaci simulovat. Autentizace proběhne pomocí **RFID čtečky**, protože většina uživatelů elektromobilu už vlastní RFID kartu.

### Síťová komunikace
Zařízení ESP32 bude komunikovat se serverem přes **HTTPS**. V případě potřeby real-time dat (např. průběžné informace o stavu nabíjení) zvážím použití **WebSocketů**.

### Platby
Po ukončení nabíjení se částka automaticky strhne z bankovního účtu uživatele, nebo z jeho přednabitého kreditu. Ceník elektřiny si stanoví vlastník nabíječky. Pravděpodobně využiji knihovnu **gopay-sdk**, ale ještě ověřím její použitelnost.

### Backend a API
Vytvořím vlastní API pomocí **FastAPI** – kvůli přehledné dokumentaci a jednoduchému testování. Je také napsané v Pythonu, ve kterém se chci zlepšovat.

### Databáze
Pro ukládání uživatelských účtů, historie nabíjení a informací o nabíječkách použiji **PostgreSQL** – robustní relační databázi dobře podporovanou v Djangu.

### Webová aplikace
Pro uživatelské rozhraní využiji **Django**, které mě zaujalo svým propojením mezi backendem a frontendem.

### Frontend framework
Pro tvorbu responzivního rozhraní mohu zvažovat buď čisté Django šablony, nebo moderní knihovny jako **React** podle rozsahu a požadavků frontendu.

### Geolokace a mapa nabíječek
Zobrazování nabíječek na mapě bude řešeno pomocí **Leaflet.js**, **Mapbox** nebo Google Maps API. Každá nabíječka bude mít přiřazené GPS souřadnice.

### Bezpečnost
- API bude chráněno **tokenovou autentizací** (např. JWT).
- Komunikace poběží přes **HTTPS**.
- Uživatelé budou mít různé **role** (např. majitel, uživatel).
- Servery budou nastaveny s ohledem na bezpečnostní zásady (CORS, CSRF, atd.).

## Stanovení cílů

1. Komunikace mezičlenu s API Solax nabíječky – mezičlen po přečtení RFID karty zahájí nabíjení a bude posílat informace o odebraných kWh na server.
3. Vytvořit responzivní web s mapou nabíječek, správou účtů, stanic a historií nabíjení.
4. Automatizované strhávání plateb z účtu nebo z kreditu.
5. Zobrazování statistik o zdroji elektřiny (síť vs. domácí fotovoltaika).

### Volitelné cíle

1. Rezervační systém nabíječek.
2. Pro nabíječky bez RFID čtečky vytvořit druhou verzi mezičlenu, který po autentizaci zprostředkuje započetí nabíjení.
2. Přidání podpory i pro jiné nabíječky s API než Solax.
3. Autentizace mobilem přes NFC – zvážit vytvoření mobilní aplikace (Android/iOS).

## Časový rozvrh
Po celou dobu projektu si budu psát pracovní verzi dokumentace, kterou potom přetvořím do publikování-schopné verze.

### Červenec
- Seznámení s API nabíjecích stanic Solax.
- Zprovoznění RFID čtečky.
- Schopnost ovládat nabíjení přes API.

### Srpen
- Programování mezičlenu (ESP32 nebo Raspberry).
- Vývoj vlastního backendu a API serveru.
- Odesílání údajů o nabíjení (ID stanice, ID uživatele, kWh, čas začátku a konce).

### Září
- Zprovoznění platební logiky (GoPay nebo kreditní systém).

### Říjen
- Tvorba frontendové části webu.
- Zobrazování statistik o původu elektřiny.

### Listopad
- Rezerva pro skluz nebo volitelné cíle.
- Úprava dokumentace

### Prosinec
- Příprava prezentace

## Získání potřebných znalostí a dovedností

- Seznámím se s API nabíjecích stanic (Solax i jiné).
- Zdokonalím se v Pythonu, tvorbě API (FastAPI), databází (PostgreSQL) a práci s Djangu.
- Naučím se pracovat s hardwarem (ESP32, RFID).
- Zvážím vývoj mobilní aplikace (pokud bude nutná autentizace přes NFC).