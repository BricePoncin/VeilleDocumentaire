import requests
from bs4 import BeautifulSoup
import os
import subprocess
from datetime import datetime

# Liste des sites à scraper avec leurs paramètres spécifiques
SITES = [
    {
        "name": "Legifrance",
        "url": "https://www.legifrance.gouv.fr/recherche",
        "params": {"query": ""},  # Les mots-clés seront ajoutés dynamiquement
        "date_selector": "span.date",  # Sélecteur CSS pour la date (à adapter)
        "link_selector": "a[href$='.pdf']"  # Sélecteur CSS pour les liens PDF
    },
    {
        "name": "ANSM",
        "url": "https://ansm.sante.fr/recherche",
        "params": {"search": ""},  # Les mots-clés seront ajoutés dynamiquement
        "date_selector": ".date",  # Sélecteur CSS pour la date (à adapter)
        "link_selector": "a[href$='.pdf']"  # Sélecteur CSS pour les liens PDF
    }
    # Ajoute d'autres sites ici si nécessaire
]

# Liste des mots-clés à rechercher
KEYWORDS = ["nom de la molécule", "paracétamol", "essai clinique"]  # Remplace par tes mots-clés

def scrape_site(site, keyword):
    params = site["params"]
    params[list(params.keys())[0]] = keyword  # Ajouter le mot-clé au paramètre de recherche

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(site["url"], params=params, headers=headers)
    response.encoding = 'utf-8'
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    pdf_links = []
    for link in soup.select(site["link_selector"]):
        title = link.text.strip()

        # Vérifier si le mot-clé est dans le titre (optionnel)
        if any(kw.lower() in title.lower() for kw in KEYWORDS):

            # Trouver la date associée au lien
            parent = link.find_parent('div') or link.find_parent('article') or link.find_parent('li')
            date = "Inconnue"
            if parent and site["date_selector"]:
                date_element = parent.select_one(site["date_selector"])
                if date_element:
                    date = date_element.text.strip()

            pdf_links.append({
                'title': title,
                'url': link['href'] if link['href'].startswith('http') else f"{site['url'].split('/recherche')[0]}{link['href']}",
                'source': site["name"],
                'date': date
            })
    return pdf_links

def scrape_all_sites():
    all_links = []
    for site in SITES:
        for keyword in KEYWORDS:
            print(f"Recherche sur {site['name']} avec le mot-clé : {keyword}")
            try:
                links = scrape_site(site, keyword)
                all_links.extend(links)
            except Exception as e:
                print(f"Erreur lors du scraping de {site['name']} avec le mot-clé {keyword}: {e}")
    return all_links

def generate_html(data, filename="index.html"):
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Veille Documentaire</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            a { color: #007BFF; text-decoration: none; }
            button { background-color: #007BFF; color: white; border: none; padding: 10px 20px; cursor: pointer; margin-bottom: 10px; }
            button:hover { background-color: #0056b3; }
            .keyword-filter { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>Veille Documentaire</h1>

        <div class="keyword-filter">
            <label for="keyword-select">Filtrer par mot-clé :</label>
            <select id="keyword-select" onchange="filterByKeyword()">
                <option value="">Tous</option>
    """

    # Ajouter les options de filtrage par mot-clé
    for keyword in KEYWORDS:
        html_content += f'<option value="{keyword.lower()}">{keyword}</option>'

    html_content += """
            </select>
        </div>

        <button id="downloadAllBtn" onclick="downloadAll()">Tout télécharger</button>

        <table id="documentsTable">
            <thead>
                <tr>
                    <th>Sélectionner</th>
                    <th>Titre</th>
                    <th>Source</th>
                    <th>Date</th>
                    <th>Lien</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in data:
        html_content += f"""
                <tr class="keyword-{item['title'].lower()}">
                    <td><input type="checkbox" class="doc-checkbox" data-url="{item['url']}"></td>
                    <td>{item['title']}</td>
                    <td>{item['source']}</td>
                    <td>{item['date']}</td>
                    <td><a href="{item['url']}" target="_blank">Télécharger</a></td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>

        <script>
            function downloadAll() {
                const checkboxes = document.querySelectorAll('.doc-checkbox:checked');
                checkboxes.forEach(checkbox => {
                    const url = checkbox.getAttribute('data-url');
                    window.open(url, '_blank');
                });
            }

            function filterByKeyword() {
                const selectedKeyword = document.getElementById('keyword-select').value;
                const rows = document.querySelectorAll('#documentsTable tbody tr');

                rows.forEach(row => {
                    if (selectedKeyword === '' || row.classList.contains(`keyword-${selectedKeyword}`)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        </script>
    </body>
    </html>
    """

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def push_to_github():
    try:
        subprocess.run(['git', 'add', 'index.html'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Mise à jour de la veille documentaire'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Modifications poussées vers GitHub avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la mise à jour Git: {e}")

if __name__ == "__main__":
    try:
        data = scrape_all_sites()
        if data:
            generate_html(data)
            push_to_github()
            print(f"Trouvé {len(data)} documents.")
        else:
            print("Aucun document PDF trouvé.")
    except Exception as e:
        print(f"Erreur lors de l'exécution du script: {e}")
