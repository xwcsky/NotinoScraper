import json
import webbrowser
import os

def pobierz_top_5(nazwa_pliku):
    try:
        with open(nazwa_pliku, 'r', encoding='utf-8') as f:
            dane = json.load(f)
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku {nazwa_pliku}!")
        return []

    def wylicz_punkty(produkt):
        ocena_str = produkt.get("ocena")
        opinie_str = produkt.get("liczba_opinii")

        # Zamiana oceny "4,8" na liczbę zmiennoprzecinkową 4.8
        try:
            ocena = float(ocena_str.replace(',', '.')) if ocena_str else 0.0
        except ValueError:
            ocena = 0.0

        # Zabezpieczenie przed brakiem opinii
        try:
            opinie = int(opinie_str) if opinie_str else 0
        except ValueError:
            opinie = 0

        # Zwracamy krotkę: najpierw sortuje po ocenie, jak jest remis to po liczbie opinii
        return (ocena, opinie)

    # Odrzucamy produkty, które w ogóle nie mają opinii/ocen
    dane_z_ocenami = [p for p in dane if p.get("ocena") is not None]
    
    # Sortujemy od najlepszych (reverse=True)
    posortowane = sorted(dane_z_ocenami, key=wylicz_punkty, reverse=True)
    
    return posortowane[:5]

# Wczytujemy dane
top_damskie = pobierz_top_5("perfumy_damskie.json")
top_meskie = pobierz_top_5("perfumy_meskie.json")

# Generujemy piękny kod strony HTML z użyciem CSS
html = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Ranking Top 5 Perfum</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 0; padding: 30px; }
        h1 { text-align: center; color: #2c3e50; font-size: 2.5em; margin-bottom: 40px; }
        .container { display: flex; justify-content: center; gap: 40px; max-width: 1400px; margin: auto; }
        .column { width: 45%; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
        h2 { border-bottom: 3px solid #eee; padding-bottom: 15px; margin-top: 0; }
        .womens h2 { color: #e83e8c; }
        .mens h2 { color: #007bff; }
        .product { border-bottom: 1px solid #f1f1f1; padding: 20px 0; position: relative; }
        .product:last-child { border-bottom: none; }
        .brand { font-weight: 700; color: #888; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px; }
        .name { font-size: 1.3em; margin: 8px 0; color: #2c3e50; text-decoration: none; display: block; font-weight: 600;}
        .name:hover { color: #e83e8c; }
        .mens .name:hover { color: #007bff; }
        .stats { color: #555; font-size: 0.95em; margin-top: 8px; }
        .rating { font-weight: bold; color: #ffc107; font-size: 1.1em; }
        .price { position: absolute; right: 0; top: 20px; font-weight: 800; color: #28a745; font-size: 1.2em; background: #e8f5e9; padding: 5px 12px; border-radius: 20px; }
        .place { position: absolute; left: -15px; top: 20px; background: #343a40; color: white; width: 30px; height: 30px; text-align: center; line-height: 30px; border-radius: 50%; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🏆 Złoty Ranking Notino (Na bazie Twoich danych!) 🏆</h1>
    <div class="container">
        <div class="column womens">
            <h2>🌸 Najlepsze Damskie</h2>
"""

for i, p in enumerate(top_damskie, 1):
    html += f"""
            <div class="product">
                <div class="place">{i}</div>
                <div class="brand">{p.get('marka', 'Brak marki')}</div>
                <a href="{p.get('link', '#')}" target="_blank" class="name">{p.get('nazwa', 'Brak nazwy')}</a>
                <div class="price">{p.get('cena', '?')} zł</div>
                <div class="stats">Ocena: <span class="rating">⭐ {p.get('ocena', '0')}</span> (Głosów: {p.get('liczba_opinii', '0')})</div>
            </div>
    """

html += """
        </div>
        <div class="column mens">
            <h2>🕴️ Najlepsze Męskie</h2>
"""

for i, p in enumerate(top_meskie, 1):
    html += f"""
            <div class="product">
                <div class="place">{i}</div>
                <div class="brand">{p.get('marka', 'Brak marki')}</div>
                <a href="{p.get('link', '#')}" target="_blank" class="name">{p.get('nazwa', 'Brak nazwy')}</a>
                <div class="price">{p.get('cena', '?')} zł</div>
                <div class="stats">Ocena: <span class="rating">⭐ {p.get('ocena', '0')}</span> (Głosów: {p.get('liczba_opinii', '0')})</div>
            </div>
    """

html += """
        </div>
    </div>
</body>
</html>
"""

# Zapisanie do pliku i odpalenie w przeglądarce
sciezka_pliku = os.path.abspath("ranking_notino.html")
with open(sciezka_pliku, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Gotowe! Generowanie zakończone sukcesem.")
print("🌐 Otwieram przeglądarkę...")
webbrowser.open(f"file://{sciezka_pliku}")