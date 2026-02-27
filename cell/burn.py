from core.identity import CoreIdentity

def compute_burn(delta_S, S, oscillation, C_t, identity: CoreIdentity):
    α1, α2, α3 = identity.burn_weights
    return (
        α1 * (delta_S / max(S, 1)) +
        α2 * oscillation +
        α3 * (C_t / identity.E_i)
    )
