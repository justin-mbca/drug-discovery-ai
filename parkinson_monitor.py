
import re
from typing import List, Dict, Set, Tuple
import sqlite3

class ParkinsonResearchMonitor:
    def __init__(self, config_file: str = 'config.json'):
        self.load_config(config_file)
        self.setup_database()
        self.gene_symbols = self.load_gene_symbols()
    # ...existing methods only...

# ===========================================================
# Reusable functions for notebook import (module level)
# ===========================================================

    def fetch_pubmed_articles(self) -> List[Dict]:
        gene_pattern = re.compile(r'\b(' + '|'.join(all_aliases) + r')\b', re.IGNORECASE)
        for article in root.findall('.//PubmedArticle'):
            try:
                title = article.findtext('.//ArticleTitle') or ''
                abstract = article.findtext('.//Abstract/AbstractText') or ''
                authors = ', '.join([
                    a.findtext('LastName', '') + ' ' + a.findtext('Initials', '')
                    for a in article.findall('.//Author') if a.find('LastName') is not None
                ])
                pubdate = article.findtext('.//PubDate/Year') or today.year
                pmid = article.findtext('.//PMID')
                url = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
                # Expanded gene mention extraction (case-insensitive, aliases, word boundaries)
                text = title + ' ' + abstract
                matches = gene_pattern.findall(text)
                gene_mentions = list(set([alias_to_symbol[m.lower()] for m in matches if m.lower() in alias_to_symbol]))
                print(f"PMID: {pmid}\nTitle: {title}\nAbstract: {abstract[:120]}...\nMatched genes: {gene_mentions}\n---")
                score = sum(title.lower().count(term.lower()) + abstract.lower().count(term.lower()) for term in pd_terms)
                articles.append({
                    'external_id': pmid,
                    'title': title,
                    'abstract': abstract,
                    'authors': authors,
                    'publication_date': pubdate,
                    'url': url,
                    'keywords': '',
                    'gene_mentions': ', '.join(gene_mentions),
                    'relevance_score': score
                })
            except Exception as e:
                print(f"Error parsing article: {e}")
        return articles
        
    def extract_genes_from_abstracts(self, abstracts):
        alias_to_symbol = {}
        all_aliases = []
        for symbol, aliases in self.gene_aliases.items():
            alias_to_symbol[symbol.lower()] = symbol
            for alias in aliases:
                all_aliases.append(re.escape(alias))
                alias_to_symbol[alias.lower()] = symbol
        gene_pattern = re.compile(r'\b(' + '|'.join(all_aliases) + r')\b', re.IGNORECASE)
        gene_candidates = set()
        for text in abstracts:
            matches = gene_pattern.findall(text)
            gene_candidates.update([alias_to_symbol[m.lower()] for m in matches if m.lower() in alias_to_symbol])
        return list(gene_candidates)
            
    def fetch_clinical_trials(self):
        print("Fetching ClinicalTrials.gov trials...")
        import requests
        from datetime import datetime, timedelta
        lookback_days = self.config['monitoring'].get('lookback_days', 7)
        today = datetime.now()
        # Use new v2 API endpoint and parameters
        fields = [
            'NCTId', 'BriefTitle', 'Phase', 'OverallStatus',
            'StartDate', 'CompletionDate', 'Condition'
        ]
        query = 'disease'
        base_url = 'https://clinicaltrials.gov/api/v2/studies'
        params = {
            'query.term': query,
            'fields': ','.join(fields),
            'format': 'json',
            'pageSize': 30
        }
        print(f"Requesting: {base_url} with params {params}")
        r = requests.get(base_url, params=params)
        try:
            data = r.json()
        except Exception as e:
            print(f"ClinicalTrials.gov API did not return JSON. Status: {r.status_code}")
            print("Response text:", r.text[:1000])
            return []
        studies = data.get('studies', [])
        print(f"Fetched {len(studies)} studies from API.")
        if len(studies) == 0:
            print("Raw API response:", str(data)[:1000])
        trials = []
        for s in studies:
            try:
                idmod = s.get('protocolSection', {}).get('identificationModule', {})
                statmod = s.get('protocolSection', {}).get('statusModule', {})
                condmod = s.get('protocolSection', {}).get('conditionsModule', {})
                trial_id = idmod.get('nctId', '')
                title = idmod.get('briefTitle', '')
                phase = statmod.get('phase', '')
                status = statmod.get('overallStatus', '')
                interventions = ''  # Not included in fields
                targets = ', '.join(condmod.get('conditions', [])) if condmod.get('conditions') else ''
                start_date = statmod.get('startDateStruct', {}).get('date', '')
                completion_date = statmod.get('completionDateStruct', {}).get('date', '')
                url = f'https://clinicaltrials.gov/ct2/show/{trial_id}' if trial_id else ''
                trial = {
                    'trial_id': trial_id,
                    'title': title,
                    'phase': phase,
                    'status': status,
                    'interventions': interventions,
                    'targets': targets,
                    'start_date': start_date,
                    'completion_date': completion_date,
                    'url': url
                }
                print(f"Parsed trial: {trial}")
                trials.append(trial)
            except Exception as e:
                print(f"Error parsing trial: {e}")
        print(f"Returning {len(trials)} trials.")
        return trials
 
    def validate_genes_with_hgnc(self, gene_list):
        # Load HGNC symbols from file
        hgnc_path = 'data/hgnc_complete_set.txt'
        hgnc_df = pd.read_csv(hgnc_path, sep='\t', low_memory=False)
        symbol_col = 'symbol'
        hgnc_symbols = set(hgnc_df[symbol_col].astype(str).str.upper())
        validated = [g for g in gene_list if g.upper() in hgnc_symbols]
        return validated
   
    def load_config(self, config_file: str):
        default_config = {
            # ...existing code...

            # Reusable functions for notebook import (module level)


        }
        # Load config from file if exists, else use default
        import os, json
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config


    def load_gene_symbols(self) -> Set[str]:
        # Expanded with aliases and protein names for robust matching
        self.gene_aliases = {
            "SNCA": ["SNCA", "α-synuclein", "alpha-synuclein", "alpha synuclein", "PARK1"],
            "LRRK2": ["LRRK2", "leucine-rich repeat kinase 2", "PARK8"],
            "PARK2": ["PARK2", "parkin"],
            "PINK1": ["PINK1"],
            "DJ1": ["DJ-1", "DJ1", "PARK7"],
            "GBA": ["GBA", "glucocerebrosidase"],
            "MAPT": ["MAPT", "tau"],
            "VPS35": ["VPS35"],
            "ATP13A2": ["ATP13A2", "PARK9"],
            "FBXO7": ["FBXO7", "PARK15"],
            "PLA2G6": ["PLA2G6", "PARK14"],
            "UCHL1": ["UCHL1"],
            "HTRA2": ["HTRA2"],
            "GCH1": ["GCH1"],
            "TH": ["TH"],
            "COMT": ["COMT"],
            "MAOB": ["MAOB"],
            "DRD2": ["DRD2"],
            "NLRP3": ["NLRP3"],
            "SIRT1": ["SIRT1"],
            "SIRT2": ["SIRT2"],
            "PRKN": ["PRKN"],
            "SNCAIP": ["SNCAIP"],
            "LRP10": ["LRP10"]
        }
        # Return just the gene symbols for legacy code
        return set(self.gene_aliases.keys())


    def setup_database(self):
        self.conn = sqlite3.connect('parkinson_research.db')
        cursor = self.conn.cursor()
        cursor.execute('''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    external_id TEXT UNIQUE,
    title TEXT,
    abstract TEXT,
    authors TEXT,
    publication_date DATE,
    url TEXT,
    keywords TEXT,
    gene_mentions TEXT,
    relevance_score REAL,
    processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
        cursor.execute('''
CREATE TABLE IF NOT EXISTS clinical_trials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trial_id TEXT UNIQUE,
    title TEXT,
    phase TEXT,
    status TEXT,
    interventions TEXT,
    targets TEXT,
    start_date DATE,
    completion_date DATE,
    url TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
        cursor.execute('''
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT,
    content TEXT,
    priority INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent BOOLEAN DEFAULT 0
)
''')
        self.conn.commit()

    def run_daily_monitoring(self):
        print("Running daily monitoring...")
        articles = self.fetch_pubmed_articles()
        trials = self.fetch_clinical_trials()
        biorxiv = self.fetch_biorxiv_articles()
        # Save to DB
        self.save_articles(articles, source='pubmed')
        self.save_articles(biorxiv, source='biorxiv')
        self.save_trials(trials)
        # Send email report
        self.send_email_report()
        print("Monitoring complete.")

    def start_scheduled_monitoring(self):
        interval = self.config['monitoring'].get('check_interval_hours', 24)
        print(f"Starting scheduled monitoring every {interval} hours...")
        schedule.every(interval).hours.do(self.run_daily_monitoring)
        while True:
            schedule.run_pending()
            time.sleep(60)


    def fetch_biorxiv_articles(self):
        # Placeholder: implement actual bioRxiv/medRxiv logic
        print("Fetching bioRxiv/medRxiv articles...")
        return []

    def save_articles(self, articles, source):
        print(f"Saving {len(articles)} articles from {source}...")
        if not articles:
            return
        with sqlite3.connect('parkinson_research.db') as conn:
            cursor = conn.cursor()
            for a in articles:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO articles
                        (source, external_id, title, abstract, authors, publication_date, url, keywords, gene_mentions, relevance_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        source,
                        a.get('external_id'),
                        a.get('title'),
                        a.get('abstract'),
                        a.get('authors'),
                        a.get('publication_date'),
                        a.get('url'),
                        a.get('keywords'),
                        a.get('gene_mentions'),
                        a.get('relevance_score')
                    ))
                except Exception as e:
                    print(f"Error saving article: {e}")
            conn.commit()

    def save_trials(self, trials):
        print(f"Saving {len(trials)} clinical trials...")
        if not trials:
            print("No trials to save.")
            return
        with sqlite3.connect('parkinson_research.db') as conn:
            cursor = conn.cursor()
            for t in trials:
                try:
                    print(f"Inserting trial_id: {t.get('trial_id')}, title: {t.get('title')}")
                    cursor.execute('''
                        INSERT OR IGNORE INTO clinical_trials
                        (trial_id, title, phase, status, interventions, targets, start_date, completion_date, url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        t.get('trial_id'),
                        t.get('title'),
                        t.get('phase'),
                        t.get('status'),
                        t.get('interventions'),
                        t.get('targets'),
                        t.get('start_date'),
                        t.get('completion_date'),
                        t.get('url')
                    ))
                except Exception as e:
                    print(f"Error saving trial: {e} | Data: {t}")
            conn.commit()
        print("Done saving clinical trials.")

    def send_email_report(self):
        # Placeholder: implement email logic
        print("Sending email report...")

	# (All other methods from your provided system should be inserted here)

# =============== WEB DASHBOARD (Flask) ===============
from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

app = Flask(__name__)
monitor = ParkinsonResearchMonitor()

@app.route('/')
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/summary')
def get_summary():
    with sqlite3.connect('parkinson_research.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM articles')
        total_articles = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM clinical_trials')
        total_trials = cursor.fetchone()[0]
        cursor.execute('SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC')
        source_data = cursor.fetchall()
        cursor.execute('SELECT gene_mentions FROM articles WHERE gene_mentions != ""')
        all_genes = []
        for row in cursor.fetchall():
            all_genes.extend(row[0].split(', '))
        from collections import Counter
        gene_counts = Counter(all_genes)
        top_genes = dict(gene_counts.most_common(15))
    return jsonify({
        'total_articles': total_articles,
        'total_trials': total_trials,
        'sources': dict(source_data),
        'top_genes': top_genes,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/recent_articles')
def get_recent_articles():
    with sqlite3.connect('parkinson_research.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title, authors, url, relevance_score, gene_mentions, source, publication_date FROM articles ORDER BY processed_date DESC LIMIT 20')
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'title': row[0],
                'authors': row[1],
                'url': row[2],
                'relevance_score': row[3],
                'genes': row[4].split(', ') if row[4] else [],
                'source': row[5],
                'publication_date': row[6]
            })
    return jsonify(articles)

@app.route('/api/clinical_trials')
def get_clinical_trials():
    with sqlite3.connect('parkinson_research.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title, phase, status, targets, url FROM clinical_trials ORDER BY last_updated DESC LIMIT 15')
        trials = []
        for row in cursor.fetchall():
            trials.append({
                'title': row[0],
                'phase': row[1],
                'status': row[2],
                'targets': row[3].split(', ') if row[3] else [],
                'url': row[4]
            })
    return jsonify(trials)

def create_visualizations():
    cursor = monitor.conn.cursor()
    cursor.execute('SELECT DATE(processed_date) as date, COUNT(*) as count FROM articles GROUP BY DATE(processed_date) ORDER BY date DESC LIMIT 30')
    date_data = cursor.fetchall()
    dates = [row[0] for row in date_data][::-1]
    counts = [row[1] for row in date_data][::-1]
    fig1 = go.Figure(data=go.Scatter(x=dates, y=counts, mode='lines+markers'))
    fig1.update_layout(title='Articles Collected Over Time', xaxis_title='Date', yaxis_title='Number of Articles')
    cursor.execute('SELECT gene_mentions FROM articles WHERE gene_mentions != ""')
    gene_pairs = {}
    for row in cursor.fetchall():
        genes = row[0].split(', ')
        for i in range(len(genes)):
            for j in range(i+1, len(genes)):
                pair = tuple(sorted([genes[i], genes[j]]))
                gene_pairs[pair] = gene_pairs.get(pair, 0) + 1
    nodes = set()
    edges = []
    for (gene1, gene2), weight in list(gene_pairs.items())[:20]:
        nodes.add(gene1)
        nodes.add(gene2)
        edges.append((gene1, gene2, weight))
    fig1.write_html("visualizations/articles_over_time.html")
    cursor.execute('SELECT gene_mentions FROM articles WHERE gene_mentions != ""')
    all_genes = []
    for row in cursor.fetchall():
        all_genes.extend(row[0].split(', '))
    from collections import Counter
    gene_counts = Counter(all_genes)
    top_genes = gene_counts.most_common(15)
    genes = [gene for gene, _ in top_genes]
    counts = [count for _, count in top_genes]
    fig2 = go.Figure(data=go.Bar(x=genes, y=counts))
    fig2.update_layout(title='Top Gene Targets Mentioned', xaxis_title='Gene', yaxis_title='Mentions')
    fig2.write_html("visualizations/top_genes.html")

# =============== MAIN EXECUTION ===============
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parkinson\'s Disease Research Monitor')
    parser.add_argument('--mode', choices=['monitor', 'dashboard', 'once'], default='once', help='Run mode')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--port', type=int, default=5000, help='Dashboard port (default: 5000)')
    args = parser.parse_args()
    monitor = ParkinsonResearchMonitor(args.config)