import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import glob

def process_movies():
    input_files = glob.glob('input*.json')

    if not input_files:
        return

    scraper = cloudscraper.create_scraper()

    for file_path in input_files:
        output_file = file_path.replace('input', 'output')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        except:
            continue

        updated_movies = []

        for movie in input_data.get('movies', []):
            title = movie.get('title')
            watch_url = movie.get('links', {}).get('watch')

            movie_entry = movie.copy()

            try:
                resp = scraper.get(watch_url, timeout=20)
                soup = BeautifulSoup(resp.text, 'html.parser')
                iframe = soup.find('iframe')
                
                if iframe and 'src' in iframe.attrs:
                    iframe_src = iframe['src']
                    iframe_res = scraper.get(iframe_src, headers={'Referer': watch_url}, timeout=20)
                    
                    m3u8_match = re.search(r'file\s*:\s*"(https?://[^"]+\.m3u8[^"]*)"', iframe_res.text)
                    
                    if m3u8_match:
                        movie_entry["stream_url"] = m3u8_match.group(1)
                        movie_entry["headers"] = {"Referer": "https://speedostream1.com/"}
                        updated_movies.append(movie_entry)
            except:
                continue

        if updated_movies:
            final_output = {"movies": updated_movies}
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_movies()
