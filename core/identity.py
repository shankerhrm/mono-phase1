from dataclasses import dataclass

@dataclass(frozen=True)
class CoreIdentity:
    E_i: float      # energy intake per cycle
    E_m: float      # max energy
    E_s: float      # survival threshold
    E_r: float      # reproduction threshold

    c_B: float
    c_M: float
    c_R: float
    c_K: float
    c_P: float

    burn_weights: tuple  # (α1, α2, α3)
    mutation_rate: float

    # Additional experimental parameters
    initial_energy: float  # E₀
    basal_burn: float      # β
    action_cost_multiplier: float  # α
    initial_structure_size: int    # S₀
    decay_rate: float      # δ
    split_ratio: float      # σ

    # Quiescence parameters
    E_quiescence: float    # energy threshold for quiescence
    S_quiescence: int      # structure threshold for quiescence
