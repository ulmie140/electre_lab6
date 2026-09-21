from flask import Flask, render_template, request, jsonify
from src.domain.models import Alternative, Criterion
from src.services.electre_mcdm import ElectreDecisionMaker

app = Flask(__name__)

criteria_list = [
    Criterion("exp", "Опыт работы (лет)"),
    Criterion("net", "Торговая сеть (баллы)"),
    Criterion("rep", "Репутация (баллы)")
]

# Перевод качественных оценок в числа по шкале Харрингтона
# Сеть: "развитая" -> 0.8, "средняя" -> 0.5, "хуже ТФ4" -> 0.4, "лучше ТФ4" -> 0.6
# Репутация: "сомнительная" -> 0.3, "средняя" -> 0.5, "хорошая" -> 0.7
firms = [
    Alternative("F1", "ТФ1", {"exp": 5, "net": 0.8, "rep": 0.3}),
    Alternative("F2", "ТФ2", {"exp": 2, "net": 0.8, "rep": 0.7}),
    Alternative("F3", "ТФ3", {"exp": 6, "net": 0.8, "rep": 0.5}),
    Alternative("F4", "ТФ4", {"exp": 5, "net": 0.5, "rep": 0.7}),
    Alternative("F5", "ТФ5", {"exp": 7, "net": 0.4, "rep": 0.5}),
    Alternative("F6", "ТФ6", {"exp": 4, "net": 0.6, "rep": 0.7})
]

# Эксперт 1: Репутация (3), Опыт (2), Сеть (1)
# Эксперт 2: Репутация (3), Сеть (2), Опыт (1)
expert_ranks = [
    {"rep": 3, "exp": 2, "net": 1},
    {"rep": 3, "exp": 1, "net": 2}
]

decision_maker = ElectreDecisionMaker(firms, criteria_list)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.json
    c_thresh = float(data.get("c_threshold", 0.5))
    d_thresh = float(data.get("d_threshold", 0.5))
    use_pareto = bool(data.get("use_pareto", True))

    try:
        active_firms = decision_maker.get_pareto_optimal_set() if use_pareto else firms
        pareto_names = [f.name for f in active_firms]

        weights = decision_maker.calculate_weights_rank_method(expert_ranks)
        electre_results = decision_maker.apply_electre(active_firms, weights, c_thresh, d_thresh)

        return jsonify({
            "pareto_set": pareto_names,
            "weights": weights,
            "electre": electre_results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400