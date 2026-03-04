from core.identity import CoreIdentity

class Energy:
    def __init__(self, E0, identity: CoreIdentity):
        self.E = E0
        self.id = identity

    def update(self, C_t, intake=None, extra_burn=0):
        if intake is None:
            intake = self.id.E_i
        self.E = min(float(self.id.E_m), self.E + intake - C_t - self.id.basal_burn - extra_burn)
        self.E = max(0.0, self.E)
