# DrawSVG Benutzeroberfläche

Dieses Projekt stellt eine einfache grafische Oberfläche zum Zeichnen von SVG-Formen mit [PySide6](https://doc.qt.io/qtforpython/) bereit.\
Sie können verschiedene Objekte über die Palette per Drag & Drop auf die Zeichenfläche ziehen und dort anpassen.

## Möglichkeiten der UI
* **Formen anlegen:** Rechtecke, Kreise, Linien und Text aus der Palette auf die Leinwand ziehen.
* **Anpassen per Maus:**
  * `Strg` + Mausrad verändert die Größe selektierter Objekte.
  * `Alt` + Mausrad rotiert selektierte Objekte.
* **Kontextmenü:** Rechtsklick auf ein Objekt erlaubt das Ändern von Farben, Linienbreite sowie Textgröße.
* **Export/Import:** Im Menü `Datei` können Szenen als `drawsvg`-Python-Dateien exportiert oder wieder geladen werden.
* **Canvas löschen:** Über `Edit` → `Canvas delete` lassen sich alle Objekte entfernen.

## Voraussetzungen
Zur Ausführung wird **Python 3.10** benötigt. Die benötigten Pakete befinden sich in der Datei `requirements.txt` und lassen sich mit:

```bash
python -m pip install -r requirements.txt
```

installieren.

## Starten der Anwendung
Nach der Installation der Abhängigkeiten kann die Anwendung mit folgendem Befehl gestartet werden:

```bash
python src/main.py
```

