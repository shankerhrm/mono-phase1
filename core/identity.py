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

    # Maintenance parameters (Phase-2)
    S_critical: int        # structural threshold for maintenance trigger
    E_maintenance_min: float  # minimum energy for maintenance
    repair_efficiency: float  # α for repair calculation

    # Reproduction parameters (Phase-4)
    E_repro: float         # energy threshold for reproduction
    S_repro: int           # structure threshold for reproduction
    r: float               # split ratio for child energy/structure
    C_divide: float        # fixed energy cost for division
    epsilon_E: float       # stability threshold for ΔE
    epsilon_S: float       # stability threshold for ΔS
    stability_window: int  # N cycles for stability check
    child_survival_cycles: int  # M cycles child must survive
    birth_stress_cycles: int     # K cycles of elevated burn

    # Regulator parameters (Phase-5, heritable)
    regulator_alpha: float    # α for heavy repair threshold
    regulator_beta: float     # β for light repair threshold
    regulator_gamma: float    # γ for conserve energy threshold
    regulator_mutation_rate: float  # mutation rate for regulator params

    # Phase-6 time parameters
    alpha_O: float            # environmental decay rate for τ_failure
    def get_tau_failure(self):
        """Environmental decay clock."""
        return self.alpha_O
    tau_max: float            # maximum coordination delay (hard cutoff)
    k_coord: float            # constant for τ_coord ∝ k * log(N)
    tau_sense: float          # base sensing latency
    tau_signal: float         # base signaling latency
    tau_act: float            # base action latency
    latency_drift_rate: float # rate of latency increase per cycle (aging)
    size_penalty_factor: float # additional latency per cell beyond base

    # Phase-6C prediction parameters
    prediction_horizon: float   # Δt_predict, time into future for estimation

    # Phase-6D modular self parameters
    number_of_predictive_modules: int  # number of local predictive modules
    arbitration_delay: float           # additional delay for hierarchical arbitration
    module_horizon_adapt_rate: float   # rate modules adapt prediction horizon
    global_integrator_capacity: float  # arbitration capacity

    # Phase-6E conflict resolution and scene change
    arbitration_mechanism: str         # 'temporal_sequencing'
    scene_change_threshold: float      # Θ for error threshold triggering scene change
    scene_min_duration: int            # minimum cycles per scene

    kappa_pred: float = 0.0           # predictive confidence weight
