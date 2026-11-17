"""Module with definitions of considered species"""
import random

class Probability:
    """Descriptor ensuring probability values stay within [0.0, 1.0]."""

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        clamped = min(1.0, max(0.0, float(value)))
        setattr(obj, self.private_name, clamped)


class Creature:
    p_death = Probability()
    p_reproduce = Probability()

    def __init__(self, p_death: float, p_reproduce: float):
        self.alive: bool = True
        self.p_death = p_death
        self.p_reproduce = p_reproduce

    def kill(self):
        """Kills (i.e. alive=False) the creature with probability p_death."""
        if random.random() < self.p_death:
            self.alive = False

    def reproduce(self):
        """Returns new instance of Creature with probability p_reproduce (otherwise None)."""
        if self.alive and (random.random() < self.p_reproduce):
            return self.__class__(p_death=self.p_death, p_reproduce=self.p_reproduce)
        return None


class Prey(Creature):
    p_hunt = Probability()

    def __init__(self, p_death: float, p_reproduce: float, p_hunt: float):
        super().__init__(p_death, p_reproduce)
        self.p_hunt = p_hunt

    def reproduce(self):
        if self.alive and (random.random() < self.p_reproduce):
            return Prey(
                p_death=self.p_death,
                p_reproduce=self.p_reproduce,
                p_hunt=self.p_hunt,
            )
        return None


class Predator(Creature):
    p_death_hungry = Probability()

    def __init__(
        self,
        p_death: float,
        p_reproduce: float,
        hungry: bool = True,
        p_death_hungry: float = 0.9,
    ):
        super().__init__(p_death, p_reproduce)
        self.hungry = hungry
        self.p_death_hungry = p_death_hungry

    def hunt(self, prey: Prey):
        """Attempts to hunt a living prey; marks predator as fed on success."""
        if prey.alive and (random.random() < prey.p_hunt):
            prey.alive = False
            self.hungry = False

    def reproduce(self):
        """Predator reproduces only if alive and fed (not hungry)."""
        if not self.hungry:
            return super().reproduce()
        return None

    def kill(self):
        """Applies higher mortality if hungry, then resets hunger for the next cycle."""
        if self.hungry:
            if random.random() < self.p_death_hungry:
                self.alive = False
        else:
            if random.random() < self.p_death:
                self.alive = False
            self.hungry = True

from dataclasses import dataclass
import matplotlib.pyplot as plt

@dataclass
class HistoryElement:
    prey: int
    predators: int


class Population:

    def __init__(self, population_data, parameters):
        self._instances = set()

        for species, number in population_data.items():
            for _ in range(number):
                creature = species(**parameters[species])
                self._instances.add(creature)

        self.history = [self.n]

    def hunting(self):
        predators = [c for c in self._instances if isinstance(c, Predator) and c.alive]
        preys = [c for c in self._instances if isinstance(c, Prey) and c.alive]

        random.shuffle(predators)
        random.shuffle(preys)

        for predator, prey in zip(predators, preys):
            predator.hunt(prey)

    def natural_selection(self):
        # 1. Polowanie (najedzone drapieżniki mogą się potem rozmnożyć)
        self.hunting()

        # 2. Rozmnażanie żywych osobników
        newborns = set()
        for creature in self._instances:
            if creature.alive:
                child = creature.reproduce()
                if child is not None:
                    newborns.add(child)

        # 3. Śmiertelność naturalna / z głodu
        for creature in self._instances:
            if creature.alive:
                creature.kill()

        # 4. Aktualizacja populacji i zapis historii
        self._instances = {creature for creature in self._instances if creature.alive}
        self._instances.update(newborns)

        self.history.append(self.n)

    def simulate(self, steps: int):
        """Przeprowadza symulację przez określoną liczbę kroków (pokoleń)."""
        for _ in range(steps):
            if self.n.prey == 0 and self.n.predators == 0:
                break
            self.natural_selection()

    def plot_history(self):
        """Wykres liniowy zmian liczebności populacji w czasie."""
        plt.figure(figsize=(8, 5))
        plt.plot([h.prey for h in self.history], label="Prey")
        plt.plot([h.predators for h in self.history], label="Predators")
        plt.xlabel("Step (generation)")
        plt.ylabel("Population size")
        plt.title("Population history")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_histograms(self, bins: int = 15):
        """Histogram rozkładu wielkości populacji oraz parametrów żyjących osobników."""
        prey_counts = [h.prey for h in self.history]
        predator_counts = [h.predators for h in self.history]

        prey_reproduce = [c.p_reproduce for c in self._instances if isinstance(c, Prey)]
        pred_reproduce = [c.p_reproduce for c in self._instances if isinstance(c, Predator)]

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Panel 1: Histogram liczebności populacji w trakcie symulacji
        axes[0].hist(prey_counts, bins=bins, alpha=0.6, label="Prey")
        axes[0].hist(predator_counts, bins=bins, alpha=0.6, label="Predators")
        axes[0].set_xlabel("Population size")
        axes[0].set_ylabel("Frequency (number of steps)")
        axes[0].set_title("Distribution of population sizes")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Panel 2: Histogram prawdopodobieństwa rozmnażania żyjących osobników
        axes[1].hist(prey_reproduce, bins=bins, range=(0, 1), alpha=0.6, label="Prey")
        axes[1].hist(pred_reproduce, bins=bins, range=(0, 1), alpha=0.6, label="Predators")
        axes[1].set_xlabel("p_reproduce")
        axes[1].set_ylabel("Number of alive individuals")
        axes[1].set_title("Distribution of p_reproduce (surviving)")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    @property
    def n(self):
        prey = sum(1 for c in self._instances if isinstance(c, Prey) and c.alive)
        predators = sum(1 for c in self._instances if isinstance(c, Predator) and c.alive)

        return HistoryElement(prey, predators)


if __name__ == "__main__":
    population_data = {
        Prey: 200,
        Predator: 50,
    }

    parameters = {
        Prey: {
            "p_death": 0.1,
            "p_reproduce": 0.25,
            "p_hunt": 0.75,
        },
        Predator: {
            "p_death": 0.15,
            "p_reproduce": 0.5,
        },
    }

    sim = Population(population_data, parameters)
    sim.simulate(steps=100)
    sim.plot_history()
    sim.plot_histograms()