from flask import Flask, render_template, request, redirect, url_for
from models.intent_model import init_db, classify_intent, get_history_as_dataframe

app = Flask(__name__)

# Inicializa o banco ao subir a aplicação
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    confidence = None
    
    if request.method == "POST":
        user_text = request.form.get("text", "")
        if user_text.strip():
            prediction, confidence = classify_intent(user_text)

    # Recupera histórico recente usando Pandas em formato de dicionário para o HTML
    df_history = get_history_as_dataframe()
    history = df_history.to_dict(orient="records") if not df_history.empty else []

    return render_template("index.html", prediction=prediction, confidence=confidence, history=history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)