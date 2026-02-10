"""
How to run the dashboard:

    python parkinson_monitor_backup.py --mode dashboard --port 5050

This will start the dashboard server at http://localhost:5050
You can then open your browser and navigate to that address to use the dashboard.
"""
import re
from typing import List, Dict, Set, Tuple
import sqlite3
import pandas as pd
from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

app = Flask(__name__)
monitor = None  # Will be initialized in main block

class ParkinsonResearchMonitor:
    def get_summary(self):
        """Return a summary of the current research status."""
        num_articles = 0
        num_trials = 0
        try:
            articles = self.fetch_pubmed_articles()
            num_articles = len(articles)
        except Exception:
            pass
        try:
            trials = self.fetch_clinical_trials()
            num_trials = len(trials)
        except Exception:
            pass
        summary = f"Articles found: {num_articles}\nClinical trials found: {num_trials}"
        return summary

    def __init__(self, config_file: str = 'config.json'):
        self.load_config(config_file)
        self.setup_database()
        self.gene_symbols = self.load_gene_symbols()
    # ...existing methods only...

    # ===========================================================
    # Reusable functions for notebook import (module level)
    # ===========================================================

    def fetch_pubmed_articles(self, published_after: str = None, disease: str = 'Parkinson disease') -> List[Dict]:
        # Load HGNC symbols from file
        hgnc_path = 'data/hgnc_complete_set.txt'
        import pandas as pd
        hgnc_df = pd.read_csv(hgnc_path, sep='\t', low_memory=False)
        symbol_col = 'symbol'
        hgnc_symbols = set(hgnc_df[symbol_col].astype(str).str.upper())
        # List of common English words that are also gene symbols to ignore as gene matches
        common_words = {"IMPACT", "SET", "TIME", "REST", "HOPE", "BEST", "IDEAL", "ACT", "CARE", "HOME", "GAP", "MAP", "ACE", "AGE", "ART", "BASE", "BOND", "CASH", "COIN", "CORE", "COST", "CURE", "DASH", "DATE", "DREAM", "ECHO", "FIRM", "FLEX", "FOCUS", "GIFT", "GOAL", "GRACE", "HERO", "IDEA", "IMAGE", "INDEX", "JUMP", "LINK", "LIST", "LOG", "MARK", "MATCH", "MINT", "MODE", "MORAL", "MOTION", "MOVE", "NAME", "NOTE", "PACE", "PEAK", "PEARL", "PEP", "PICK", "PINE", "PITCH", "POINT", "PRIME", "PRINT", "PRIZE", "RACE", "RANGE", "RANK", "RATE", "REACT", "RECORD", "REF", "RING", "RISE", "RISK", "ROLE", "ROOT", "RULE", "RUN", "SCORE", "SENSE", "SHAPE", "SHIFT", "SHINE", "SIGN", "SKY", "SMART", "SMILE", "SONG", "SOUND", "SPACE", "SPARK", "SPEED", "SPIN", "SPOT", "STAR", "STATE", "STEP", "STICK", "STOCK", "STONE", "STORY", "STYLE", "SUM", "SUN", "SURF", "SWING", "TASTE", "TEAM", "TONE", "TOUCH", "TRACK", "TRADE", "TRAIL", "TREND", "TRUST", "VALUE", "VIEW", "VISION", "VOICE", "WAVE", "WISH", "WORK", "ZONE"}
        gene_pattern = re.compile(r'\b(' + '|'.join([re.escape(sym) for sym in hgnc_symbols]) + r')\b', re.IGNORECASE)
        articles = []
        # Fetch PubMed articles using Entrez API
        import requests
        import xml.etree.ElementTree as ET
        from datetime import datetime
        today = datetime.now()
        query = disease
        # Add date filter if provided (format: YYYY/MM/DD)
        mindate = ''
        maxdate = ''
        if published_after:
            # Ensure mindate and maxdate are in YYYY-MM-DD format for PubMed
            mindate = published_after.replace('/', '-')
            maxdate = today.strftime('%Y-%m-%d')
        # Build PubMed API URL with mindate/maxdate if provided
        if mindate and maxdate:
            url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&mindate={mindate}&maxdate={maxdate}&retmax=200&sort=pub+date'
        else:
            url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=200&sort=pub+date'
        print(f"[DEBUG] PubMed API URL: {url}")
        print(f"[DEBUG] mindate: {mindate}, maxdate: {maxdate}, query: {query}")
        r = requests.get(url)
        idlist = []
        try:
            root_search = ET.fromstring(r.text)
            idlist = [id_elem.text for id_elem in root_search.findall('.//Id')]
        except Exception as e:
            print(f"Error parsing PubMed search XML: {e}")
        if not idlist:
            print("[DEBUG] No PubMed IDs found for efetch.")
            return articles
        # Fetch details for each article
        ids_str = ','.join(idlist)
        url_fetch = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids_str}&retmode=xml'
        r2 = requests.get(url_fetch)
        try:
            root = ET.fromstring(r2.text)
        except Exception as e:
            print(f"Error parsing PubMed fetch XML: {e}")
            print(f"[DEBUG] efetch URL: {url_fetch}")
            print(f"[DEBUG] efetch response (first 500 chars): {r2.text[:500]}")
            return articles
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
                # Gene mention extraction using HGNC symbols
                text = title + ' ' + abstract
                matches = gene_pattern.findall(text)
                gene_mentions = list(set([
                    m.upper() for m in matches
                    if m.upper() in hgnc_symbols and m.upper() not in common_words
                ]))
                articles.append({
                    'external_id': pmid,
                    'title': title,
                    'abstract': abstract,
                    'authors': authors,
                    'publication_date': pubdate,
                    'url': url,
                    'keywords': '',
                    'gene_mentions': ', '.join(gene_mentions)
                })
            except Exception as e:
                print(f"[DEBUG] Error parsing article XML: {e}")
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
            
    def fetch_clinical_trials(self, start_date: str = None, disease: str = 'parkinson'):
        import requests
        from datetime import datetime
        today = datetime.now()
        base_url = 'https://clinicaltrials.gov/api/v2/studies'
        params = {
            'query.term': disease,
            'format': 'json',
            'pageSize': 200
        }
        r = requests.get(base_url, params=params)
        try:
            data = r.json()
        except Exception as e:
            return []
        studies = data.get('studies', [])
        trials = []
        for s in studies:
            try:
                prot = s.get('protocolSection', {})
                idmod = prot.get('identificationModule', {})
                statmod = prot.get('statusModule', {})
                designmod = prot.get('designModule', {})
                trial_id = idmod.get('nctId', '')
                title = idmod.get('briefTitle', '')
                phase = ''
                if isinstance(designmod.get('phases', None), list) and designmod['phases']:
                    phase = ', '.join([str(p) for p in designmod['phases'] if p])
                status = statmod.get('overallStatus', '')
                interventions = ''  # Not included in fields
                # Try to get conditions/targets if present
                targets = ''
                condmod = prot.get('conditionsModule', {})
                if 'conditions' in condmod and condmod['conditions']:
                    targets = ', '.join([str(c) for c in condmod['conditions'] if c])
                start_date_val = ''
                if 'startDateStruct' in statmod:
                    start_date_val = statmod['startDateStruct'].get('date', '')
                completion_date = ''
                if 'completionDateStruct' in statmod:
                    completion_date = statmod['completionDateStruct'].get('date', '')
                url = f'https://clinicaltrials.gov/ct2/show/{trial_id}' if trial_id else ''
                trial = {
                    'trial_id': trial_id,
                    'title': title,
                    'phase': phase,
                    'status': status,
                    'interventions': interventions,
                    'targets': targets,
                    'start_date': start_date_val,
                    'completion_date': completion_date,
                    'url': url
                }
                # Filter by start_date if provided
                if start_date and start_date_val:
                    try:
                        # Try full date first
                        try:
                            trial_start = datetime.strptime(start_date_val, '%Y-%m-%d')
                        except ValueError:
                            # Try year-month format
                            trial_start = datetime.strptime(start_date_val, '%Y-%m')
                        filter_date = datetime.strptime(start_date, '%Y-%m-%d')
                        if trial_start < filter_date:
                            continue
                    except Exception as e:
                        print(f"Error parsing trial start date: {e} | Value: {start_date_val}")
                trials.append(trial)
            except Exception as e:
                print(f"Error parsing trial: {e} | Raw: {s}")
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

# =============== WEB DASHBOARD (Flask) ===============
from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

app = Flask(__name__)
monitor = None  # Will be initialized in main block

from flask import request
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    from datetime import datetime, timedelta
    # Default: last 7 days
    default_days = 7
    date_str = ''
    disease_options = [
        ('parkinson', "Parkinson's Disease"),
        ('alzheimers', "Alzheimer's Disease"),
        ('huntington', "Huntington's Disease"),
        ('als', "ALS (Amyotrophic Lateral Sclerosis)"),
        ('multiple sclerosis', "Multiple Sclerosis"),
        ('epilepsy', "Epilepsy"),
        ('stroke', "Stroke"),
        ('brain tumor', "Brain Tumor"),
        ('glioblastoma', "Glioblastoma"),
        ('meningitis', "Meningitis"),
        ('encephalitis', "Encephalitis")
    ]
    selected_disease = 'parkinson'
    if request.method == "POST":
        date_str = request.form.get("published_after", "")
        selected_disease = request.form.get("disease", "parkinson")
    if not date_str:
        date_obj = datetime.now() - timedelta(days=default_days)
        date_str = date_obj.strftime("%Y-%m-%d")
    # For PubMed: YYYY/MM/DD, for trials: YYYY-MM-DD
    pubmed_date = date_str.replace('-', '/')
    # Map dropdown value to PubMed query
    disease_pubmed_map = {
        'parkinson': "Parkinson disease",
        'alzheimers': "Alzheimer disease",
        'huntington': "Huntington disease",
        'als': "Amyotrophic Lateral Sclerosis",
        'multiple sclerosis': "Multiple Sclerosis",
        'epilepsy': "Epilepsy",
        'stroke': "Stroke",
        'brain tumor': "Brain Tumor",
        'glioblastoma': "Glioblastoma",
        'meningitis': "Meningitis",
        'encephalitis': "Encephalitis"
    }
    disease_pubmed = disease_pubmed_map.get(selected_disease, "Parkinson disease")
    articles = monitor.fetch_pubmed_articles(published_after=pubmed_date, disease=disease_pubmed) if monitor else []
    trials = monitor.fetch_clinical_trials(start_date=date_str, disease=selected_disease) if monitor else []
    num_articles = len(articles)
    num_trials = len(trials)
    summary = f"Articles found: {num_articles}\nClinical trials found: {num_trials}"

    # Top target genes visualization
    import pandas as pd
    import plotly.offline as po
    import plotly.graph_objs as go
    top_genes_html = ""
    try:
        gene_mentions = []
        for a in articles:
            genes = a.get('gene_mentions', '')
            if genes:
                gene_mentions.extend([g.strip() for g in genes.split(',') if g.strip()])
        gene_counts = pd.Series(gene_mentions).value_counts().head(10)
        if not gene_counts.empty:
            gene_bar = go.Bar(x=gene_counts.index.tolist(), y=gene_counts.values.tolist())
            gene_layout = go.Layout(title='Top Validated Gene Targets')
            gene_fig = go.Figure(data=[gene_bar], layout=gene_layout)
            top_genes_html = po.plot(gene_fig, output_type='div', include_plotlyjs='cdn')
        else:
            top_genes_html = "<pre>No gene targets found in articles.</pre>"
    except Exception as e:
        top_genes_html = f"<pre>Error generating gene chart: {e}</pre>"

    # Articles table
    articles_table = "<table border='1'><tr><th>Title</th><th>PMID</th><th>Abstract</th></tr>"
    for a in articles:
        title = a.get('title','')
        url = a.get('url','')
        title_link = f"<a href='{url}' target='_blank'>{title}</a>" if url else title
        articles_table += f"<tr><td>{title_link}</td><td>{a.get('external_id','')}</td><td>{a.get('abstract','')[:200]}...</td></tr>"
    articles_table += "</table>"

    # Trials table
    trials_table = "<table border='1'><tr><th>Title</th><th>Status</th><th>Start Date</th></tr>"
    for t in trials:
        title = t.get('title','')
        url = t.get('url','')
        title_link = f"<a href='{url}' target='_blank'>{title}</a>" if url else title
        trials_table += f"<tr><td>{title_link}</td><td>{t.get('status','')}</td><td>{t.get('start_date','')}</td></tr>"
    trials_table += "</table>"

    html = f"""
    <h1>Neurodegenerative Disease Research Dashboard</h1>
    <form method='post'>
        <label for='disease'>Disease: </label>
        <select id='disease' name='disease'>
            {''.join([f"<option value='{val}' {'selected' if val == selected_disease else ''}>{label}</option>" for val, label in disease_options])}
        </select>
        <label for='published_after'>Show new articles/trials since: </label>
        <input type='date' id='published_after' name='published_after' value='{date_str}'>
        <input type='submit' value='Search'>
    </form>
    <h2>Summary</h2>
    <pre>{summary}</pre>
    <h2>Top Validated Gene Targets</h2>
    {top_genes_html}
    <h2>Recent Clinical Trials</h2>
    {trials_table}
    <h2>Latest PubMed Articles</h2>
    {articles_table}
    """
    return html
    return html
    return html
    return html
    return html
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parkinson\'s Disease Research Monitor')
    parser.add_argument('--mode', choices=['monitor', 'dashboard', 'once'], default='once', help='Run mode')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--port', type=int, default=5000, help='Dashboard port (default: 5000)')
    parser.add_argument('--filter', choices=['week', 'month'], default='week', help='Default date filter for dashboard (week or month)')
    args = parser.parse_args()
    monitor = ParkinsonResearchMonitor(args.config)
    # Set default_days based on filter
    if args.filter == 'week':
        default_days = 7
    elif args.filter == 'month':
        default_days = 30
    else:
        default_days = 7
    # Patch dashboard to use default_days
    import types
    from datetime import datetime, timedelta
    def dashboard_with_filter():
        from flask import request
        date_str = ''
        if request.method == "POST":
            date_str = request.form.get("published_after", "")
        if not date_str:
            date_obj = datetime.now() - timedelta(days=default_days)
            date_str = date_obj.strftime("%Y-%m-%d")
        pubmed_date = date_str.replace('-', '/')
        articles = monitor.fetch_pubmed_articles(published_after=pubmed_date) if monitor else []
        trials = monitor.fetch_clinical_trials(start_date=date_str) if monitor else []
        summary = monitor.get_summary() if monitor else "No summary available."
        import pandas as pd
        import plotly.offline as po
        import plotly.graph_objs as go
        top_genes_html = ""
        try:
            gene_mentions = []
            for a in articles:
                genes = a.get('gene_mentions', '')
                if genes:
                    gene_mentions.extend([g.strip() for g in genes.split(',') if g.strip()])
            gene_counts = pd.Series(gene_mentions).value_counts().head(10)
            if not gene_counts.empty:
                gene_bar = go.Bar(x=gene_counts.index.tolist(), y=gene_counts.values.tolist())
                gene_layout = go.Layout(title='Top Validated Gene Targets')
                gene_fig = go.Figure(data=[gene_bar], layout=gene_layout)
                top_genes_html = po.plot(gene_fig, output_type='div', include_plotlyjs='cdn')
            else:
                top_genes_html = "<pre>No gene targets found in articles.</pre>"
        except Exception as e:
            top_genes_html = f"<pre>Error generating gene chart: {e}</pre>"
        articles_table = "<table border='1'><tr><th>Title</th><th>PMID</th><th>Abstract</th></tr>"
        for a in articles:
            title = a.get('title','')
            url = a.get('url','')
            title_link = f"<a href='{url}' target='_blank'>{title}</a>" if url else title
            articles_table += f"<tr><td>{title_link}</td><td>{a.get('external_id','')}</td><td>{a.get('abstract','')[:200]}...</td></tr>"
        articles_table += "</table>"
        trials_table = "<table border='1'><tr><th>Title</th><th>Status</th><th>Start Date</th></tr>"
        for t in trials:
            title = t.get('title','')
            url = t.get('url','')
            title_link = f"<a href='{url}' target='_blank'>{title}</a>" if url else title
            trials_table += f"<tr><td>{title_link}</td><td>{t.get('status','')}</td><td>{t.get('start_date','')}</td></tr>"
        trials_table += "</table>"
        from datetime import datetime, timedelta
        today = datetime.now()
        last_week = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        last_month = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        html = f"""
        <h1>Parkinson's Disease Research Dashboard</h1>
        <form method='post' id='dateForm'>
            <label for='published_after'>Show new articles/trials since: </label>
            <input type='date' id='published_after' name='published_after' value='{date_str}'>
            <input type='submit' value='Search'>
            <button type='button' onclick="setDate('{last_week}')">Last week</button>
            <button type='button' onclick="setDate('{last_month}')">Last month</button>
        </form>
        <script>
        function setDate(val) {{
            document.getElementById('published_after').value = val;
            document.getElementById('dateForm').submit();
        }}
        </script>
        <h2>Summary</h2>
        <pre>{summary}</pre>
        <h2>Top Validated Gene Targets</h2>
        {top_genes_html}
        <h2>Latest PubMed Articles</h2>
        {articles_table}
        <h2>Recent Clinical Trials</h2>
        {trials_table}
        """
        return html
    if args.mode == 'monitor':
        monitor.run_daily_monitoring()
    elif args.mode == 'dashboard':
        app.run(host='0.0.0.0', port=args.port, debug=True)
    elif args.mode == 'once':
        monitor.run_daily_monitoring()
