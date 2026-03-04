import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CycleTrace:
    seed: int
    env: str
    generation: int
    cell_id: int
    parent_id: int | None
    cycle: int
    tau_action: float
    tau_cognition: float
    cog_invoked: bool
    energy_pre: float | None
    energy_post: float
    gamma_used: float
    modules_active: int


@dataclass(frozen=True)
class ReproductionTrace:
    seed: int
    env: str
    generation: int
    parent_id: int
    child_id: int
    species_defaults_applied: dict
    offspring_initial_params: dict
    yolk_size: float
    lifespan: int = 0


class Phase10Observer:
    def __init__(self, seed: int, env: str):
        self.seed = int(seed)
        self.env = str(env)
        self.generation = 0
        self.cycle_traces: list[CycleTrace] = []
        self.reproduction_traces: list[ReproductionTrace] = []
        self.violations: list[dict] = []
        self.lineage_tau: dict[float, list[float]] = {}

    def set_generation(self, generation: int):
        self.generation = int(generation)
        self.lineage_tau = {}

    def record_cycle(
        self,
        *,
        cell,
        cycle_log: dict,
        tau_action: float,
        tau_cognition: float,
        cog_invoked: bool,
        energy_pre: float | None,
        energy_post: float,
        gamma_used: float,
        modules_active: int,
    ):
        try:
            self.cycle_traces.append(
                CycleTrace(
                    seed=self.seed,
                    env=self.env,
                    generation=self.generation,
                    cell_id=int(getattr(cell, 'cell_id', -1)),
                    parent_id=getattr(cell, 'parent_id', None),
                    cycle=int(cycle_log.get('cycle', -1)),
                    tau_action=float(tau_action),
                    tau_cognition=float(tau_cognition),
                    cog_invoked=bool(cog_invoked),
                    energy_pre=None if energy_pre is None else float(energy_pre),
                    energy_post=float(energy_post),
                    gamma_used=float(gamma_used),
                    modules_active=int(modules_active),
                )
            )
        except Exception as e:
            self.emit_violation(
                code="Measurement_Backpressure",
                message="Observer measurement failed under stress",
                cell_id=cell.cell_id,
                generation=self.generation,
                cycle=cycle_log.get('cycle', -1),
                exception=str(e),
            )

        # Invariant monitor: Cognition Spam
        # If cognition is invoked but energy drops significantly (waste), flag it
        if cog_invoked and energy_pre is not None and energy_post < energy_pre * 0.95:
            self.emit_violation(
                code="COGNITION_SPAM",
                message="Cognition invoked but energy dropped significantly (potential waste)",
                cell_id=cell.cell_id,
                generation=self.generation,
                cycle=cycle_log.get('cycle', -1),
                energy_pre=energy_pre,
                energy_post=energy_post,
            )

            self.lineage_tau.setdefault(cell.initial_gamma, []).append(tau_action)

    def record_reproduction(self, *, parent, child, generation, species_memory, species_defaults_applied: dict, yolk_size: float = 0.0):
        ms_gamma = species_memory.Ms.get('gamma', 0.5)
        parent_gamma = parent.gating_threshold
        child.initial_gamma = 0.7 * ms_gamma + 0.3 * parent_gamma  # IIBA hybrid

        offspring_initial_params = {
            'module_count': int(getattr(child, 'module_count', 0)),
            'gamma': child.initial_gamma,
            'tau_budget': float(getattr(child, 'get_tau_failure', lambda: 0.0)()),
            'energy_ceiling': float(getattr(child, 'id', None).E_m) if getattr(child, 'id', None) is not None else 0.0,
            'ms_contribution': 0.7 * ms_gamma,
            'parent_contribution': 0.3 * parent_gamma
        }
        self.reproduction_traces.append(
            ReproductionTrace(
                seed=self.seed,
                env=self.env,
                generation=generation,
                parent_id=int(getattr(parent, 'cell_id', -1)),
                child_id=int(getattr(child, 'cell_id', -1)),
                species_defaults_applied={'gamma': child.initial_gamma},
                offspring_initial_params=offspring_initial_params,
                yolk_size=float(yolk_size),
                lifespan=0,
            )
        )

    def emit_violation(self, code: str, message: str, **data):
        self.violations.append({'code': str(code), 'message': str(message), **data})

    def emit_lineage_drift_violations(self):
        for gamma, taus in self.lineage_tau.items():
            if len(taus) > 1:
                mean_tau = sum(taus) / len(taus)
                if mean_tau > 0:
                    var = sum((t - mean_tau)**2 for t in taus) / len(taus)
                    std = var**0.5
                    if std / mean_tau > 0.1:
                        self.emit_violation(
                            code="LINEAGE_RUNTIME_DRIFT",
                            message=f"Lineage runtime drift for gamma {gamma:.3f}: tau std {std:.3f} > 10% of mean {mean_tau:.3f}",
                            gamma=gamma,
                            std_tau=std,
                            mean_tau=mean_tau,
                            count=len(taus),
                            generation=self.generation
                        )

def _bin_index(value: float, lo: float, hi: float, bins: int) -> int:
    if bins <= 1:
        return 0
    if value <= lo:
        return 0
    if value >= hi:
        return bins - 1
    frac = (value - lo) / max(hi - lo, 1e-12)
    idx = int(frac * bins)
    return max(0, min(bins - 1, idx))


def mutual_information_discrete(xs: list[float], ys: list[float], bins: int = 10) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0

    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)

    joint = [[0 for _ in range(bins)] for _ in range(bins)]
    x_counts = [0 for _ in range(bins)]
    y_counts = [0 for _ in range(bins)]

    n = len(xs)
    for x, y in zip(xs, ys):
        xi = _bin_index(float(x), x_lo, x_hi, bins)
        yi = _bin_index(float(y), y_lo, y_hi, bins)
        joint[xi][yi] += 1
        x_counts[xi] += 1
        y_counts[yi] += 1

    mi = 0.0
    for i in range(bins):
        for j in range(bins):
            c_xy = joint[i][j]
            if c_xy == 0:
                continue
            p_xy = c_xy / n
            p_x = x_counts[i] / n
            p_y = y_counts[j] / n
            mi += p_xy * math.log(p_xy / max(p_x * p_y, 1e-12), 2)

    return float(mi)
