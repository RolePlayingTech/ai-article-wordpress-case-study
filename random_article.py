#!/usr/bin/env python3
"""
Skrypt, który automatycznie tworzy losowy artykuł do WordPressa wykorzystując model AI.
Generuje zarówno tytuł jak i treść artykułu w jednym wywołaniu API na zróżnicowane, 
zaskakujące tematy.

Przykład użycia:
python random_article.py
python random_article.py --draft
"""

import os
import requests
import sys
from openai import OpenAI
from dotenv import load_dotenv
import random

# --------------------------------------------------------------------------------
# KONFIGURACJA TEMATÓW ARTYKUŁÓW
# --------------------------------------------------------------------------------
# Lista przykładowych tematów (używana tylko jako inspiracja dla AI)
EXAMPLE_TOPICS = [
    "Nieznane zastosowania miodu w starożytnym Egipcie",
    "Jak zwierzęta przewidują katastrofy naturalne",
    "Tajemnice mikroekspresji twarzy w komunikacji międzyludzkiej",
    "Wpływ kolorów na podejmowanie decyzji zakupowych",
    "Zapomniane wynalazki, które wyprzedziły swoją epokę",
    "Dziwne tradycje kulinarne z różnych zakątków świata",
    "Jak dźwięki wpływają na rozwój roślin",
    "Sekrety długowieczności w odizolowanych społecznościach",
    "Nieoczywiste zastosowania sztucznej inteligencji w codziennym życiu",
    "Wpływ faz księżyca na zachowanie ludzi i zwierząt",
    "Ukryte symbole w architekturze średniowiecznej",
    "Jak memy kształtują współczesną kulturę",
    "Psychologia kolorów w różnych kulturach świata",
    "Niezwykłe zjawiska pogodowe, których nie znasz",
    "Jak zmienia się ludzki mózg pod wpływem mediów społecznościowych"
]

# Przykładowe tagi dla artykułów
ARTICLE_TAGS = ["ciekawostki", "wiedza", "nauka", "kultura", "świat"]

# --------------------------------------------------------------------------------
# WCZYTANIE ZMIENNYCH ŚRODOWISKOWYCH Z PLIKU .ENV
# --------------------------------------------------------------------------------
load_dotenv()

# Sprawdzenie, czy używamy lokalnej instancji WordPress
WORDPRESS_ENV = os.getenv("WORDPRESS_ENV", "production").lower()

# Konfiguracja API
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
API_KEY = os.getenv("API_KEY")

# Ustawienie URL API na podstawie dostawcy
if os.getenv("API_BASE_URL"):
    # Jeśli API_BASE_URL jest ustawiony ręcznie, użyj go
    API_BASE_URL = os.getenv("API_BASE_URL")
else:
    # W przeciwnym razie ustaw na podstawie AI_PROVIDER
    if AI_PROVIDER == "openrouter":
        API_BASE_URL = "https://openrouter.ai/api/v1"
    else:  # domyślnie openai
        API_BASE_URL = "https://api.openai.com/v1"

# Informacje o stronie (dla OpenRouter)
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "")

# Dane dostępowe do WordPress
print(f"Używam instancji WordPress: {WORDPRESS_ENV}")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD").replace(" ", "")  # Usuwamy spacje z hasła aplikacji
WP_API_URL = os.getenv("WP_API_URL")

# Konfiguracja generowania artykułów
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "800"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Sprawdzenie, czy wszystkie wymagane zmienne środowiskowe są ustawione
required_vars = ["WP_USERNAME", "WP_PASSWORD", "WP_API_URL", "API_KEY"]

missing_vars = [var for var in required_vars if not locals().get(var)]

if missing_vars:
    print(f"Błąd: Brakujące zmienne środowiskowe: {', '.join(missing_vars)}")
    print("Upewnij się, że plik .env zawiera wszystkie wymagane zmienne.")
    exit(1)

# Inicjalizacja klienta API
print(f"Używam dostawcy AI: {AI_PROVIDER} ({API_BASE_URL})")

# Sprawdzenie, czy mamy informacje o stronie dla OpenRouter
if AI_PROVIDER == "openrouter" and (not YOUR_SITE_URL or not YOUR_SITE_NAME):
    print("Ostrzeżenie: Brak informacji o stronie (YOUR_SITE_URL, YOUR_SITE_NAME) wymaganych przez OpenRouter.")

# Inicjalizacja klienta OpenAI
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

def generate_article_with_ai():
    """
    Generuje zarówno temat, tytuł jak i treść artykułu w jednym wywołaniu API.
    Zwraca krotkę (tytuł, treść).
    """
    # Wybierz kilka przykładowych tematów jako inspirację
    sample_topics = random.sample(EXAMPLE_TOPICS, min(5, len(EXAMPLE_TOPICS)))
    examples = "\n".join([f"- {topic}" for topic in sample_topics])
    
    messages = [
        {"role": "system", "content": "Jesteś doświadczonym redaktorem, tworzącym fascynujące artykuły na różnorodne tematy. Używasz nagłówków (h2, h3), list, pogrubień i kursywy, aby tekst był czytelny i atrakcyjny. Zwracasz odpowiedzi w czystym formacie JSON bez dodatkowych znaczników Markdown."},
        {
            "role": "user",
            "content": (
                "Wymyśl oryginalny, zaskakujący temat artykułu, a następnie napisz na ten temat wyczerpujący, ciekawy i zrozumiały artykuł.\n\n"
                f"Przykłady tematów dla inspiracji (wymyśl coś nowego, nie powtarzaj tych przykładów):\n{examples}\n\n"
                f"Zwróć wynik w następującym formacie JSON:\n"
                f"{{\n"
                f'  "topic": "Wymyślony przez Ciebie temat artykułu",\n'
                f'  "title": "Chwytliwy tytuł artykułu (nie dłuższy niż 10 słów)",\n'
                f'  "content": "Pełna treść artykułu w formacie Markdown"\n'
                f"}}\n\n"
                f"Wskazówki dotyczące treści:\n"
                f"- Podziel tekst na sekcje z nagłówkami (## dla h2, ### dla h3)\n"
                f"- Używaj **pogrubień** dla ważnych terminów i *kursywy* dla wyróżnień\n"
                f"- Dodaj listy punktowane tam, gdzie to ma sens\n"
                f"- Na końcu dodaj krótkie podsumowanie\n"
                f"- Pisz w stylu luźnym, ale profesjonalnym\n"
                f"- Zadbaj o to, by artykuł był fascynujący i zawierał nieoczywiste informacje\n"
            )
        }
    ]

    try:
        # Przygotowanie parametrów dla API
        params = {
            "model": AI_MODEL,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "response_format": {"type": "json_object"}
        }
        
        # Dodanie nagłówków dla OpenRouter
        extra_headers = {}
        if AI_PROVIDER == "openrouter":
            extra_headers = {
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            }
        
        # Wywołanie API
        completion = client.chat.completions.create(
            **params,
            extra_headers=extra_headers if AI_PROVIDER == "openrouter" else {},
            extra_body={}
        )

        # Pobranie wygenerowanego tekstu jako JSON
        import json
        response_content = completion.choices[0].message.content
        
        # Dodaj obsługę błędów parsowania JSON
        try:
            # Znajdź początek i koniec obiektu JSON
            start_idx = response_content.find("{")
            end_idx = response_content.rfind("}")
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                # Wyodrębnij tylko prawidłowy obiekt JSON
                json_content = response_content[start_idx:end_idx+1]
                article_data = json.loads(json_content)
                
                # Wyświetl wygenerowany temat
                print(f"Wygenerowany temat: {article_data.get('topic')}")
                return article_data.get("title"), article_data.get("content")
            else:
                # Jeśli nie można znaleźć prawidłowego obiektu JSON
                print(f"Nie można znaleźć prawidłowego obiektu JSON w odpowiedzi.")
                print(f"Otrzymana odpowiedź: {response_content[:200]}...")
                return None, None
                
        except json.JSONDecodeError as json_err:
            print(f"Błąd parsowania JSON: {str(json_err)}")
            print(f"Otrzymana odpowiedź: {response_content[:200]}...")  # Pokaż początek odpowiedzi
            
            # Próba naprawy odpowiedzi JSON
            try:
                # Usuń znaki nowej linii i tabulatory
                clean_content = response_content.replace("\n", " ").replace("\t", " ")
                
                # Znajdź początek i koniec obiektu JSON
                start_idx = clean_content.find("{")
                end_idx = clean_content.rfind("}")
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    # Wyodrębnij tylko prawidłowy obiekt JSON
                    json_content = clean_content[start_idx:end_idx+1]
                    article_data = json.loads(json_content)
                    
                    print(f"Udało się naprawić JSON")
                    print(f"Wygenerowany temat: {article_data.get('topic')}")
                    return article_data.get("title"), article_data.get("content")
            except Exception as e:
                print(f"Nie udało się naprawić JSON: {str(e)}")
            
            # Jeśli nie udało się naprawić, zwróć None
            return None, None
            
    except Exception as e:
        print(f"Błąd podczas generowania artykułu: {str(e)}")
        return None, None

def format_article_content(title, content):
    """
    Formatuje treść artykułu do HTML zgodnego ze strukturą WordPress.
    Zapewnia odpowiednie formatowanie paragrafów i nagłówków.
    """
    # Najpierw czyścimy treść z niepotrzebnych znaków
    content = content.strip()
    
    # Usuwamy znaki # z początku linii i zamieniamy je na odpowiednie tagi HTML
    lines = content.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Przetwarzanie nagłówków
        if line.startswith('# '):
            formatted_lines.append(f'<h2 class="wp-block-heading">{line[2:]}</h2>')
        elif line.startswith('## '):
            formatted_lines.append(f'<h3 class="wp-block-heading">{line[3:]}</h3>')
        elif line.startswith('### '):
            formatted_lines.append(f'<h4 class="wp-block-heading">{line[4:]}</h4>')
        # Przetwarzanie list
        elif line.startswith('- '):
            # Sprawdź, czy to pierwszy element listy
            if i == 0 or not lines[i-1].startswith('- '):
                formatted_lines.append('<ul class="wp-block-list">')
            formatted_lines.append(f'<li>{line[2:]}</li>')
            # Sprawdź, czy to ostatni element listy
            if i == len(lines) - 1 or not lines[i+1].startswith('- '):
                formatted_lines.append('</ul>')
        # Puste linie zamieniamy na znaczniki końca akapitu
        elif not line:
            if formatted_lines and not formatted_lines[-1].endswith('</p>') and not formatted_lines[-1].endswith('</h2>') and not formatted_lines[-1].endswith('</h3>') and not formatted_lines[-1].endswith('</h4>') and not formatted_lines[-1].endswith('</ul>') and not formatted_lines[-1] == '<ul class="wp-block-list">':
                formatted_lines.append('</p>')
            continue
        # Zwykły tekst traktujemy jako akapit
        else:
            # Sprawdź, czy to początek nowego akapitu
            if i == 0 or not lines[i-1] or lines[i-1].endswith('</h2>') or lines[i-1].endswith('</h3>') or lines[i-1].endswith('</h4>') or lines[i-1].endswith('</ul>'):
                formatted_lines.append('<p>')
            formatted_lines.append(line)
    
    # Upewnij się, że ostatni akapit jest zamknięty
    if formatted_lines and not formatted_lines[-1].endswith('</p>') and not formatted_lines[-1].endswith('</h2>') and not formatted_lines[-1].endswith('</h3>') and not formatted_lines[-1].endswith('</h4>') and not formatted_lines[-1].endswith('</ul>'):
        formatted_lines.append('</p>')
    
    # Łączymy linie z powrotem w tekst
    html_content = '\n'.join(formatted_lines)
    
    # Przetwarzanie pogrubień i kursyw
    # Pogrubienia
    while '**' in html_content:
        if html_content.count('**') >= 2:
            html_content = html_content.replace('**', '<strong>', 1)
            html_content = html_content.replace('**', '</strong>', 1)
        else:
            break
    
    # Kursywa
    while '*' in html_content:
        if html_content.count('*') >= 2:
            html_content = html_content.replace('*', '<em>', 1)
            html_content = html_content.replace('*', '</em>', 1)
        else:
            break
    
    # Czyszczenie - usuwamy podwójne tagi i puste akapity
    html_content = html_content.replace('<p></p>', '')
    html_content = html_content.replace('<p>\n</p>', '')
    
    # Dodanie klasy WordPress do głównego kontenera
    formatted_article = f"""
<div class="entry-content wp-block-post-content has-global-padding is-layout-constrained wp-block-post-content-is-layout-constrained">
{html_content}
</div>
    """
    
    return formatted_article

def publish_article_to_wordpress(title, content, tags=None, status="publish"):
    """
    Publikuje artykuł w WordPressie przez REST API.
    title   - tytuł artykułu
    content - treść artykułu (HTML lub zwykły tekst)
    tags    - tablica stringów lub docelowo ID tagów (tutaj uproszczone)
    status  - publish / draft / future
    
    Zwraca: (bool, str) - (sukces, link do artykułu)
    """
    # Przygotowujemy dane do wysłania
    post_data = {
        "title": title,
        "content": content,
        "status": status
    }
    
    # Dodaj tagi, jeśli zostały podane - najpierw pobierz ich ID
    if tags and isinstance(tags, list) and len(tags) > 0:
        try:
            # Pobierz istniejące tagi z WordPressa
            tags_response = requests.get(f"{WP_API_URL.replace('posts', 'tags')}", auth=(WP_USERNAME, WP_PASSWORD))
            
            if tags_response.status_code == 200:
                existing_tags = tags_response.json()
                tag_ids = []
                
                # Znajdź ID dla każdego tagu
                for tag_name in tags:
                    tag_id = None
                    # Sprawdź, czy tag już istnieje
                    for existing_tag in existing_tags:
                        if existing_tag.get('name', '').lower() == tag_name.lower():
                            tag_id = existing_tag.get('id')
                            break
                    
                    # Jeśli tag nie istnieje, utwórz go
                    if not tag_id:
                        create_tag_response = requests.post(
                            f"{WP_API_URL.replace('posts', 'tags')}", 
                            json={"name": tag_name},
                            auth=(WP_USERNAME, WP_PASSWORD)
                        )
                        if create_tag_response.status_code in (200, 201):
                            tag_id = create_tag_response.json().get('id')
                    
                    # Dodaj ID tagu do listy
                    if tag_id:
                        tag_ids.append(tag_id)
                
                # Dodaj ID tagów do danych artykułu
                if tag_ids:
                    post_data["tags"] = tag_ids
            else:
                print(f"Nie udało się pobrać tagów. Kod odpowiedzi: {tags_response.status_code}")
        except Exception as e:
            print(f"Błąd podczas przetwarzania tagów: {str(e)}")
            # Kontynuuj bez tagów

    try:
        # Uwierzytelnianie - Basic Auth z hasłem bez spacji
        auth = (WP_USERNAME, WP_PASSWORD)

        # Żądanie POST do WordPressa
        response = requests.post(WP_API_URL, json=post_data, auth=auth)

        if response.status_code in (200, 201):
            # Pobierz link do artykułu z odpowiedzi
            response_data = response.json()
            article_link = response_data.get('link', '')
            
            print(f"Artykuł '{title}' opublikowany pomyślnie.")
            print(f"Link do artykułu: {article_link}")
            
            return True, article_link
        else:
            print(f"Nie udało się opublikować artykułu '{title}'. Kod odpowiedzi: {response.status_code}")
            print("Treść odpowiedzi:", response.text)
            return False, ""
    except Exception as e:
        print(f"Błąd podczas publikowania artykułu: {str(e)}")
        return False, ""

def main():
    # Sprawdzenie argumentów wiersza poleceń
    status = "publish"
    if len(sys.argv) > 1 and sys.argv[1] == "--draft":
        status = "draft"
    
    # Generowanie artykułu (temat, tytuł i treść) w jednym wywołaniu
    print("\nGeneruję artykuł na losowy temat...")
    title, content = generate_article_with_ai()
    
    if not title or not content:
        print("Nie udało się wygenerować artykułu. Kończę działanie.")
        return
    
    print(f"Wygenerowany tytuł: {title}")
    
    # Formatowanie treści w HTML z lepszym stylem
    formatted_content = format_article_content(title, content)
    
    # Publikowanie artykułu w WordPressie
    success, article_link = publish_article_to_wordpress(
        title, 
        formatted_content, 
        tags=ARTICLE_TAGS, 
        status=status
    )
    
    if success:
        print("Artykuł został pomyślnie opublikowany. Kończę działanie.")
    else:
        print("Nie udało się opublikować artykułu. Kończę działanie.")

if __name__ == "__main__":
    main()
