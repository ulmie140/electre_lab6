from typing import List, Dict
from src.domain.models import Alternative, Criterion


class ElectreDecisionMaker:
    """Математическое ядро для многокритериального анализа."""

    def __init__(self, alternatives: List[Alternative], criteria: List[Criterion]):
        self.alternatives = alternatives
        self.criteria = criteria

    def get_pareto_optimal_set(self) -> List[Alternative]:
        """Отбор Парето-оптимальных решений."""
        pareto_set = []
        for i, alt_i in enumerate(self.alternatives):
            is_dominated = False
            for j, alt_j in enumerate(self.alternatives):
                if i == j:
                    continue

                strictly_better_in_one = False
                better_or_equal_in_all = True

                for crit in self.criteria:
                    val_i = alt_i.scores[crit.id]
                    val_j = alt_j.scores[crit.id]

                    if crit.is_maximize:
                        if val_j < val_i: better_or_equal_in_all = False
                        if val_j > val_i: strictly_better_in_one = True
                    else:
                        if val_j > val_i: better_or_equal_in_all = False
                        if val_j < val_i: strictly_better_in_one = True

                if better_or_equal_in_all and strictly_better_in_one:
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_set.append(alt_i)

        return pareto_set

    def calculate_weights_rank_method(self, expert_ranks: List[Dict[str, int]]) -> Dict[str, float]:
        """Вычисление весов критериев методом ранга."""
        sum_scores = {crit.id: 0.0 for crit in self.criteria}
        for ranks in expert_ranks:
            for crit_id, rank in ranks.items():
                sum_scores[crit_id] += rank

        total_sum = sum(sum_scores.values())
        return {crit_id: score / total_sum for crit_id, score in sum_scores.items()}

    def apply_electre(self, active_alternatives: List[Alternative], weights: Dict[str, float], c_threshold: float,
                      d_threshold: float) -> dict:
        """Применение метода ЭЛЕКТРА I."""
        n = len(active_alternatives)

        normalized = []
        for alt in active_alternatives:
            norm_scores = {}
            for crit in self.criteria:
                max_val = max([a.scores[crit.id] for a in active_alternatives])
                val = alt.scores[crit.id]
                norm_scores[crit.id] = val / max_val if max_val != 0 else 0
            normalized.append(norm_scores)

        c_matrix = [[0.0] * n for _ in range(n)]
        d_matrix = [[0.0] * n for _ in range(n)]
        kernel = []

        for i in range(n):
            for j in range(n):
                if i == j: continue

                c_val = 0.0
                max_d = 0.0

                for crit in self.criteria:
                    weight = weights[crit.id]
                    val_i = normalized[i][crit.id]
                    val_j = normalized[j][crit.id]

                    if val_i >= val_j:
                        c_val += weight
                    else:
                        diff = val_j - val_i
                        if diff > max_d: max_d = diff

                c_matrix[i][j] = round(c_val, 3)
                d_matrix[i][j] = round(max_d, 3)

        is_dominated = [False] * n
        for i in range(n):
            for j in range(n):
                if i != j:
                    if c_matrix[i][j] >= c_threshold and d_matrix[i][j] <= d_threshold:
                        is_dominated[j] = True

        for i in range(n):
            if not is_dominated[i]:
                kernel.append(active_alternatives[i].name)

        return {
            "alternatives": [a.name for a in active_alternatives],
            "kernel": kernel if kernel else ["Нет подходящих альтернатив"]
        }