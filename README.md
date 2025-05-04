# Sdílené nabíječky elektromobilů
## Volba tématu
Chtěl bych vytvořit systém, který by dovolil lidem sdílet své domovní nabíječky elektromobilů ostatním podobně jako Airbnb sdílí obydlí.
## Analýza problému
### Nápad
Když jsem hledal, jestli něco takového existuje tak v česku bylo provděpodobně pár pokusů, ale stránku už nefungují. V zahraničí už nějaké projekty existují, například https://www.goplugable.com/ nebo https://www.pluginn.app/en/. Go Plugable ale nabízí kompletní stanice. Tomu bych se chtěl vyhnout a chtěl bych využívat nabíjecí stanice, které už uživatel doma vlastní.
## Výběr postupu a technologií
Toto jsou postupy a technologie, které bych chtěl v projektu využít.
### Autentizace
K tomu bych chtěl využít esp32 nebo Rasberr Pi Pico, které by dělalo prostředníka mezi API nabíjecí stanice nebo v případě nepodporované nabíjecí stanice takové API nahrazovalo. Využívali by se RFID karty, které už vlastník elektroauta většinou má. Po autentizaci uživatele, může začít nabíjení.
### Platby
Po ukončení nabíjení se částka automaticky strhne z bankovního účtu uživatele, nebo z nabitého kreditu na uživatelském účtu. Ceník elektřiny si stanoví provozovatel nabíjecí stanice.
## Stanovení cílů
1. Komunikace mezičlenu s API Solax nabíječky - mezičlen podle získaných informací z rfid čtečky zahájí nabíjení a bude komunikovat se serverem aplikace a odesílat data o odebraných kW.
2. Pro nabíječky bez RFID čtečky vytvořit druhou verzi mezičlenu, který bude tuto komunikaci zprostředkovávat místo nabíječky a pošle nabíječce po autentizaci informaci, aby započala nabíjení.
3. Vytvořit responzivní webové stránky s mapou nabíječek a se správou uživatelských účtu, vlastněných nabíjecích stanic a s výpisem historie nabíjení.
4. Automatické strhávání z bankovního účtu nebo z nahraného kreditu.
5. Zobrazování statistiky o zdroji elektřiny, kterou si uživatel nabil auto (poměr mezi elektřinou ze sítě oproti domácí fotovoltaice)
### Volitelné cíle:
1. Rezervační systém nabíječek
2. Přidání podpory i pro jiné nabíječky než Solax
3. Možnost autentizace mobilem s NFC (nutnost tvorby Android nebo IOS aplikace) Zvážit jestli neudělat plnohodnotnou aplikaci, kdybych už měl nějakou dělat.
## Časový rozvrh
### Červenec
- Seznámení s API od Solax nabíjecí stanice
- Schopnost vyčíst informace z RFID čtečky na nabíjecí stanici
- Schopnost zapnout a vypnout nabíjení přes API dotazy
### Srpen
- Programování mezičlenu
- Naprogramování vlastního serveru s databází a API, který bude ukládat informace o uživatelských účtech a mezičlen na něho bude posílat informace o nabíjení (id nabíječky, id nabíjejícího, počet kW, čas a datum začátku a konce nabíjení)
### Září
- Sprovoznění backendu pro okamžité platby z účtu nebo z nabitého kreditu
### Říjen
- Tvorba frontentu - přehledného responzivního webu
- Zobrazování statistik o původu elektřiny
### Listopad
- Případná rezerva pro časový skluz
- Volitelné cíle
### Prosinec
- vytváření prezentace projektu
## Získání potřebných znalostí a dovedností
- Seznámím se s API nabíjecích stanic Solax (možná i jiných)
- Zdokonalím se v tvorbě API, backendové i frontendové části webových aplikacích
- Zdokonalím se v práci s hardwarem a naučím se jak fungují RFID karty
- V případě volitelných cílů se naučím tvořit mobilní aplikace.
## Volba technologií
 - ve fázi analýzy
