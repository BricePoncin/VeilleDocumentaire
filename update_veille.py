import requests
from bs4 import BeautifulSoup
import os
import subprocess

def scrape_legifrance():
    # Utiliser requests pour gérer correctement l'encodage
    url = "https://www.legifrance.gouv.fr/recherche"
    params = {"query": "nom de la molécule"}  # Remplacez par vos mots-clés

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, params=params, headers=headers)
    response.encoding = 'utf-8'  # Forcer l'encodage UTF-8
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    pdf_links = []
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pdf'):
            pdf_links.append({
                'title': link.text.strip(),
                'url': link['href'] if link['href'].startswith('http') else f"https://www.legifrance.gouv.fr{link['href']}",
                'source': 'Legifrance'
            })
    return pdf_links

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
        </style>
    </head>
    <body>
        <h1>Veille Documentaire</h1>
        <p>Liste des documents PDF trouvés :</p>

        <table>
            <thead>
                <tr>
                    <th>Titre</th>
                    <th>Source</th>
                    <th>Lien</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in data:
        html_content += f"""
                <tr>
                    <td>{item['title']}</td>
                    <td>{item['source']}</td>
                    <td><a href="{item['url']}" target="_blank">Télécharger</a></td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>
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
        data = scrape_legifrance()
        if data:
            generate_html(data)
            push_to_github()
        else:
            print("Aucun document PDF trouvé.")
    except Exception as e:
        print(f"Erreur lors de l'exécution du script: {e}")
