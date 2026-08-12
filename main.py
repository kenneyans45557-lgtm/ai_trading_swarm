import os
import requests
import smtplib
from email.mime.text import MIMEText

# 1. ZUGANGSDATEN AUS DEN SECRETS LADEN
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def send_email(subject, body):
    """Hilfsfunktion zum Senden der E-Mail-Updates"""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        
        with smtplib.SMTP_SSL('://gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("-> Info: E-Mail-Update erfolgreich gesendet!")
    except Exception as e:
        print(f"-> Fehler beim E-Mail-Versand: {e}")

def get_market_news():
    """Holt die aktuellsten weltweiten Wirtschafts- und Forex-Nachrichten"""
    print("🤖 AGENT_INSIDER startet News-Scraping...")
        url = f"https://newsapi.org{NEWS_API_KEY}"

    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])
        headlines = [a["title"] for a in articles if a.get("title")]
        return headlines
    except Exception as e:
        print(f"Fehler beim News holen: {e}")
        return []

def analyze_sentiment_with_ki(headline):
    """Nutzt das kostenlose FinBERT-Modell auf Hugging Face zur Stimmungsanalyse"""
        api_url = "https://huggingface.co"

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": headline}).json()
        
        # Falls das Modell noch im Standby ist und lädt
        if isinstance(response, dict) and "estimated_time" in response:
            return "neutral", 0.0
        
        # Wenn die Antwort eine Liste mit Listen ist, flachklopfen
        if isinstance(response, list) and len(response) > 0 and isinstance(response[0], list):
            predictions = response[0]
        elif isinstance(response, list):
            predictions = response
        else:
            return "neutral", 0.0
            
        best_pick = max(predictions, key=lambda x: x['score'])
        return best_pick['label'], best_pick['score']
    except Exception:
        return "neutral", 0.0

def main():
    print("=== START DES KI-SCHWARM-MEETINGS ===")
    print("🤖 AGENT_ORCHESTRATOR (CEO): Meeting gestartet. Prüfe globale Marktstimmung.")
    
    # News sammeln
    headlines = get_market_news()
    if not headlines:
        print("🤖 AGENT_INSIDER: Keine aktuellen Nachrichten gefunden. Meeting vertagt.")
        return

    print(f"🔎 AGENT_INSIDER: Ich habe {len(headlines)} globale Schlagzeilen analysiert:")
    
    total_score = 0
    pos_count = 0
    neg_count = 0
    
    for idx, title in enumerate(headlines, 1):
        label, score = analyze_sentiment_with_ki(title)
        print(f"   Headline {idx}: '{title[:60]}...' -> KI-Wertung: {label.upper()} ({score:.2f})")
        
        if label == "positive":
            total_score += score
            pos_count += 1
        elif label == "negative":
            total_score -= score
            neg_count += 1

    print("\n--- DISKUSSION & AUSWERTUNG ---")
    print(f"📊 AGENT_QUANT: Technische Zusammenfassung der News-Auswertung vorliegend.")
    print(f"   Positive Signale: {pos_count} | Negative Signale: {neg_count} | Sentiment-Trend: {total_score:.2f}")

    # Logik für den CEO-Entscheider
    print("\n🤖 AGENT_ORCHESTRATOR (CEO): Treffe finale Entscheidung...")
    
    if total_score > 0.5:
        decision_text = f"STARKE BULLISCHE STIMMUNG AM MARKT DETEKTIERT!\n\nDer KI-Nachrichten-Insider meldet überwiegend positive Fundamentaldaten (Trend-Score: {total_score:.2f}). Ein Einstieg in Long-Positionen wird vom Schwarm empfohlen."
        print(f"-> ENTSCHEIDUNG: {decision_text}")
        send_email("🚀 KI-SCHWARM: Bullisches Markt-Signal!", decision_text)
    elif total_score < -0.5:
        decision_text = f"STARK BÄRISCHE PANIK AM MARKT DETEKTIERT!\n\nDer KI-Nachrichten-Insider meldet negative Einschläge (Trend-Score: {total_score:.2f}). Vorsicht vor Long-Positionen. Short-Szenarien bevorzugt."
        print(f"-> ENTSCHEIDUNG: {decision_text}")
        send_email("⚠️ KI-SCHWARM: Bärisches Markt-Signal!", decision_text)
    else:
        print("-> ENTSCHEIDUNG: Marktstimmung ist neutral und unklar. Kein Trade freigegeben. Smartphone bleibt stumm.")

    print("=== MEETING BEENDET ===")

if __name__ == "__main__":
    main()
