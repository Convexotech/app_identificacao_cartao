import sqlite3
import pandas as pd
import spacy

# Carrega o modelo de linguagem do spaCy (em português)
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    # Fallback caso o modelo não esteja instalado globalmente
    import os
    os.system("python -m spacy download pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")

DB_PATH = "database.db"

def init_db():
    """Inicializa o banco SQLite com uma tabela de logs de intenções."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            intent TEXT NOT NULL,
            confidence TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def classify_intent(text):
    """
    Classificador baseado em spaCy (lematização e tokens) para intenções bancárias.
    """
    doc = nlp(text.lower())
    
    # Normaliza o texto extraindo lemas (ignora stopwords e pontuação)
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    text_lemmatized = " ".join(tokens)
    
    # Regras baseadas em palavras-chave e lemas do spaCy
    intent = "Desconhecida"
    confidence = "Baixa"

    # Regra 1: Bloquear Cartão
    if any(k in text_lemmatized for k in ["bloquear", "bloqueio", "perder", "roubar", "cartao","perdi"]):
        intent = "Bloquear Cartão"
        confidence = "Alta (spaCy Match)"
    
    # Regra 2: Segunda via de boleto
    elif any(k in text_lemmatized for k in ["boleto", "segunda", "via", "fatura", "conta", "pagar"]):
        intent = "Segunda Via de Boleto"
        confidence = "Alta (spaCy Match)"
        
    # Regra 3: Saldo / Extrato
    elif any(k in text_lemmatized for k in ["saldo", "extrato", "dinheiro", "conta"]):
        intent = "Consultar Saldo"
        confidence = "Média (spaCy Match)"

    # Salva no banco de dados SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (text, intent, confidence) VALUES (?, ?, ?)", 
                   (text, intent, confidence))
    conn.commit()
    conn.close()

    return intent, confidence

def get_history_as_dataframe():
    """Retorna os logs históricos utilizando Pandas."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT text, intent, confidence, timestamp FROM logs ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    return df