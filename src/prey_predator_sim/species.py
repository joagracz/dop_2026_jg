"""Module with definitions of considered species"""
import random

class Creature:

    alive: bool = True

    def __init__(self, p_death: float, p_reproduce: float):
        self.p_death = p_death
        self.p_reproduce = p_reproduce

    def kill(self):
        """Kills (i.e. alive=False) the creature with probability p_death"""
        if random.random() < self.p_death:
            self.alive = False

    def reproduce(self):
        """Returns new instance of Creature with probability p_reproduce (otherwise None)"""

        if self.alive and (random.random() < self.p_reproduce):

            # 1. Consider changing p_death, p_reproduce to have instances different from the parent
            # 2. TODO: Change creature class to different one.
            return Creature(p_death=self.p_death, p_reproduce=self.p_reproduce)

        return None
        
class Prey(Creature):
    """Ofiara: posiada parametr p_hunt (podatność na upolowanie)."""

    name: str = "Prey"
    p_hunt = Probability()

    def __init__(
        self,
        p_death: float = 0.05,
        p_reproduce: float = 0.25,
        p_hunt: float = 0.6,
        sigma: float = 0.02,
        alive: bool = True,
    ):
        super().__init__(p_death=p_death, p_reproduce=p_reproduce, sigma=sigma, alive=alive)
        self.p_hunt = p_hunt


class Predator(Creature):
    """Drapieżnik: zarządza stanem hungry i poluje na ofiary."""

    name: str = "Predator"
    p_death_hungry: float = 0.9

    def __init__(
        self,
        p_death: float = 0.1,
        p_reproduce: float = 0.15,
        sigma: float = 0.02,
        alive: bool = True,
        hungry: bool = True,
    ):
        super().__init__(p_death=p_death, p_reproduce=p_reproduce, sigma=sigma, alive=alive)
        self.hungry = hungry

    def hunt(self, prey: Prey):
        """Jeśli polowanie udane: prey.alive = False i hungry = False."""
        if random.random() < prey.p_hunt:
            prey.alive = False
            self.hungry = False

    def kill(self):
        """Gdy hungry == True używa p_death_hungry, w p.p. bazowego p_death."""
        prob = self.p_death_hungry if self.hungry else self.p_death
        if random.random() < prob:
            self.alive = False