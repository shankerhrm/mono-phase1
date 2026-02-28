from core.identity import CoreIdentity

class Energy:
    def __init__(self, E0, identity: CoreIdentity):
        self.E = E0
        self.id = identity

    def update(self, C_t, extra_burn=0):
        self.E = min(self.id.E_m, self.E - C_t - self.id.basal_burn - extra_burn)
        self.E = max(0, self.E)
