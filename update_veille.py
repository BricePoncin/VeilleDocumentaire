import urllib.request
from bs4 import BeautifulSoup
import os
import git

def scrape_legifrance():
    url = "https://www.legifrance.gouv.fr/recherche?query=nom+de+la+molécule"
    response = urllib.request.urlopen(url)
    html = response.read()
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
    repo = git.Repo('.')
    repo.git.add('index.html')
    repo.git.commit('-m', 'Mise à jour de la veille documentaire')
    repo.git.push()

if __name__ == "__main__":
    data = scrape_legifrance()
    generate_html(data)
    push_to_github()
    print("Page web mise à jour et poussée vers GitHub.")
