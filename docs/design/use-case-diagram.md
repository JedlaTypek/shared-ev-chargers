@startuml
left to right direction
title Use Case Diagram – Sdílené nabíječky elektromobilů

actor "Uživatel" as User
actor "Majitel nabíječky" as Owner
actor "Admin" as Admin
actor "Nabíječka (OCPP klient)" as Charger

(Registrace a přihlášení) as UC1
(Vyhledávání nabíječky včetně mapy) as UC2
(Spuštění nabíjení pomocí RFID) as UC3
(Spuštění nabíjení pomocí mobilní aplikace) as UC4
(Nabití kreditu do profilu) as UC5
(Zobrazení historie nabíjení uživatele) as UC6

(Vytvoření nabíječky) as UC7
(Správa nabíječky a konektorů) as UC8
(Úprava výkonu, ceny a typu konektoru) as UC9
(Zobrazení historie nabíjení na nabíječkách) as UC10

(Přístup k logům OCPP serveru) as UC11
(Správa uživatelských účtů) as UC12
(Monitorování provozu systému) as UC13
(Správa hlášení o chybách) as UC14

(Odeslání RFID autorizace) as UC15
(Zahájení nabíjení) as UC16
(Ukončení nabíjení) as UC17
(Odesílání dat o spotřebě) as UC18

' Vztahy – uživatel
User --> UC1
User --> UC2
User --> UC3
User --> UC4
User --> UC5
User --> UC6

' Vztahy – majitel
Owner --> UC7
Owner --> UC8
Owner --> UC9
Owner --> UC10

' Vztahy – admin
Admin --> UC11
Admin --> UC12
Admin --> UC13
Admin --> UC14

' Vztahy – nabíječka (OCPP klient)
Charger --> UC15
Charger --> UC16
Charger --> UC17
Charger --> UC18

' Vztahy mezi případy užití
UC3 --> UC15 : <<include>>
UC15 --> UC16 : <<include>>
UC17 --> UC18 : <<include>>
UC8 --> UC9 : <<extend>>

@enduml

