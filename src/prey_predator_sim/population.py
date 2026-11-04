from .species import Creature

class Population:

    _instances: set[Creature]
    history: list[int]

    def __init__(self, n: int, **kwargs):

        self._instances = set(
            [Creature(**kwargs) for _ in range(n)]
        )

        self.history = [self.n]

    def natural_selection(self):

        for creature in self._instances:
            creature.kill()

        self._instances = set([creature for creature in self._instances if creature.alive])

        # Aktualizacja historii

    def plot_history(self):
        pass

    @property
    def n(self) -> Dict[str, int]:
        """Bieżące liczebności żyjących osobników per gatunek."""
        counts = {Prey.name: 0, Predator.name: 0}
        for creature in self._instances:
            if creature.alive and creature.name in counts:
                counts[creature.name] += 1
        return counts

    def hunting(self):
        """Parowanie 1-1 drapieżników i ofiar."""
        predators = [c for c in self._instances if isinstance(c, Predator) and c.alive]
        preys = [c for c in self._instances if isinstance(c, Prey) and c.alive]

        random.shuffle(predators)
        random.shuffle(preys)

        for pred in predators:
            pred.hungry = True

        for pred, prey in zip(predators, preys):
            pred.hunt(prey)

    def natural_selection(self):
        """Jeden krok symulacji zgodny z kolejnością:
        (1) rozród wszystkich żyjących; zbierz noworodki,
        (2) hunting(),
        (3) śmiertelność (kill()) wszystkich żyjących,
        (4) zapis liczebności do history,
        (5) aktualizacja zbioru: usuń martwych, dodaj noworodki.
        """
        # (1) Rozród
        newborns: List[Creature] = []
        for creature in list(self._instances):
            if creature.alive:
                baby = creature.reproduce()
                if baby is not None:
                    newborns.append(baby)

        # (2) Polowanie
        self.hunting()

        # (3) Śmiertelność
        for creature in self._instances:
            if creature.alive:
                creature.kill()

        # (4) Zapis liczebności
        self.history.append(self.n)

        # (5) Aktualizacja zbioru
        self._instances = {c for c in self._instances if c.alive}
        self._instances.update(newborns)