from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re, csv, io, time
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

@app.route('/api/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url', '').strip()
    if not url.startswith('http'): url = 'https://' + url
    
    visited, to_visit, contacts = set(), [url], []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    while to_visit and len(visited) < 10:
        current = to_visit.pop(0)
        if current in visited: continue
        visited.add(current)
        
        try:
            r = requests.get(current, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', r.text)
            phones = re.findall(r'(?:\+33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', r.text)
            
            for i, email in enumerate(set(emails)):
                if 'example' not in email.lower():
                    contacts.append({
                        'nom': email.split('@')[0].replace('.', ' ').title(),
                        'email': email,
                        'telephone': phones[i] if i < len(phones) else '',
                        'source': current
                    })
            
            for link in soup.find_all('a', href=True)[:15]:
                new = urljoin(current, link['href'])
                if urlparse(new).netloc == urlparse(url).netloc:
                    to_visit.append(new)
            time.sleep(1)
        except: pass
    
    return jsonify({'success': True, 'contacts': contacts})

@app.route('/')
def home():
    return "API OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
