# Blackbox-Tests Html-Image-Map-Creator (GER)

| **Test Nr.** | **Testfall** | **Erwartetes Resultat** |
| --- | --- | --- |
| **1.** | (QGis.WKBPoint) Alle Features im herangezoomten „MapView“ mitsamt Infobox und Labels exportieren | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt |
| **2.** | (QGis.WKBPolygon) Alle Features im herangezoomten „MapView“ mitsamt Infobox und Labels exportieren | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt |
| **3.** | (QGis.WKBMultiPoint) Alle Features im herangezoomten „MapView“ mitsamt Infobox und Labels exportieren | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt |
| **4.** | (QGis.WKBMultiPolygon) Alle Features im herangezoomten „MapView“ mitsamt Infobox und Labels exportieren | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt |
| **5.** | Plugin wird auf Layer geöffnet mit einer ungültigen Geometrie | Fehlermeldung |
| **6.** | Plugin wird auf leeren Layer geöffnet (kein Layer selektiert) | Fehlermeldung |
| **7.** | Der Benutzer gibt einen Dateinamen und Pfad an, wo die zu generierenden Dateien gefunden werden | Die 3 Dateien werden mit dem vom Benutzer gewählten Namen unter dem vom Nutzer gewählten Pfad exportiert |
| **8.** | Der Benutzer wählt einen positiven Offset beim Label und bei der Infobox | Das Label und die Infobox werden nach unten verschoben in der exportierten Karte |
| **9.** | Der Benutzer wählt einen negativen Offset beim Label und bei der Infobox | Das Label und die Infobox werden nach oben verschoben in der exportierten Karte |
| **10.** | Der Benutzer aktiviert weder die Checkbox für das Labels noch für die Infobox | Der OK-Button wird nicht mehr anklickbar |
| **11.** | Der Benutzer aktiviert die Ceckbox für das Label aber nicht für die Infobox und startet den Export | Der Export ist erfolgreich und es erfolgt nur eine Beschriftung der Hotspots |
| **12.** | Der Benutzer aktiviert die Ceckbox für die Infobox aber nicht für das Label und startet den Export | Der Export ist erfolgreich und es erfolgt keine Beschriftung der Hotspots, beim Klick auf die Hotspots öffnet sich eine Infobox |

| **Test Nr.** | **Resultat** | **Bemerkung** | **Erfolg** |
| --- | --- | --- | --- |
| **1.** | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt | - | :+1: |
| **2.** | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt | - | :+1: |
| **3.** | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt | - | :+1: |
| **4.** | Labels und Infoboxen werden in der erstellten HTML-Datei korrekt angezeigt | - | :+1: |
| **5.** | Plugin wird auf Layer geöffnet mit einer ungültigen Geometrie | - | :+1: |
| **6.** | Plugin wird auf leeren Layer geöffnet (kein Layer selektiert) | - | :+1: |
| **7.** | Die 3 Dateien werden mit dem vom Benutzer gewählten Namen unter dem vom Nutzer gewählten Pfad exportiert | - | :+1: |
| **8.** | Das Label und die Infobox werden nach unten verschoben in der exportierten Karte | - | :+1: |
| **9.** | Das Label und die Infobox werden nach oben verschoben in der exportierten Karte | - | :+1: |
| **10.** | Der OK-Button wird nicht mehr anklickbar | - | :+1: |
| **11.** | Der Export ist erfolgreich und es erfolgt nur eine Beschriftung der Hotspots | - | :+1: |
| **12.** | Der Export ist erfolgreich und es erfolgt keine Beschriftung der Hotspots, beim Klick auf die Hotspots öffnet sich eine Infobox | - | :+1: |