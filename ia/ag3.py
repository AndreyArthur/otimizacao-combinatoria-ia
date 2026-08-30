from random import Random
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from collections.abc import Callable

import time

Individual = list[int]
Population = list[Individual]


class GeneticAlgorithm:
    def __init__(
        self,
        target: str,
        random: Random | None = None,
        elitism_rate: float = 0.05,
        selection_rate: float = 0.40,
        crossover_rate: float = 0.80,
        mutation_rate: float = 0.05,
    ) -> None:
        self._random = random or Random()
        self._target = self._str_to_individual(target)
        self._population = self._initialize_population()
        self._elitism_rate = elitism_rate
        self._selection_rate = selection_rate
        self._crossover_rate = crossover_rate
        self._mutation_rate = mutation_rate

    def _str_to_individual(self, individual: str) -> Individual:
        return [ord(c) for c in individual]

    def _individual_to_str(self, individual: Individual) -> str:
        return "".join([chr(c) for c in individual])

    def _random_gene(self) -> int:
        return self._random.randint(ord(" "), ord("~"))

    def _random_chance(self) -> float:
        return self._random.random()

    def _random_choice(self, pool: list[Individual]) -> Individual:
        return self._random.choice(pool)

    def _random_indexes(self) -> set[int]:
        count = self._random.randint(0, len(self._target))
        total = [i for i in range(len(self._target))]

        indexes: set[int] = set()

        for _ in range(count):
            indexes.add(total.pop(self._random.randint(0, len(total) - 1)))

        return indexes

    def _initialize_population(self) -> Population:
        population_size = len(self._target) * 2

        return [
            [self._random_gene() for _ in range(len(self._target))]
            for _ in range(population_size)
        ]

    def _fit_individual(self, individual: Individual) -> int:
        return sum(
            [
                (v - individual[i]) * (v - individual[i])
                for i, v in enumerate(self._target)
            ]
        )

    def _sort_population(self) -> None:
        self._population.sort(key=lambda k: self._fit_individual(k))

    def _select_elite(self) -> list[Individual]:
        count = (round(len(self._population) * self._elitism_rate) // 2) * 2

        return self._population[:count]

    def _calculate_weights(self) -> list[float]:
        weights = [
            1 / self._fit_individual(individual) for individual in self._population
        ]
        weights_sum = sum(weights)

        return [weight / weights_sum for weight in weights]

    def _roll_parent(self, weights: list[float]) -> Individual:
        chance = self._random_chance()

        index = -1
        weight_sum = 0.0
        while weight_sum < chance:
            index += 1
            weight_sum += weights[index]

        return self._population[index]

    def _select_parents(self) -> list[Individual]:
        weights = self._calculate_weights()
        count = round(len(self._population) * self._selection_rate)

        return [self._roll_parent(weights) for _ in range(count)]

    def _cross_individuals(
        self, first_parent: Individual, second_parent: Individual
    ) -> tuple[Individual, Individual]:
        first_child: Individual = [-1 for _ in range(len(first_parent))]
        second_child: Individual = [-1 for _ in range(len(second_parent))]

        chance = self._random_chance()
        if chance < self._crossover_rate:
            indexes = self._random_indexes()

            for i in range(len(first_parent)):
                if i in indexes:
                    first_child[i] = second_parent[i]
                    second_child[i] = first_parent[i]
                else:
                    first_child[i] = first_parent[i]
                    second_child[i] = second_parent[i]
        else:
            first_child = first_parent.copy()
            second_child = second_parent.copy()

        return first_child, second_child

    def _cross_parents(
        self, parents: list[Individual], children_count: int
    ) -> list[Individual]:
        children: list[Individual] = []

        while len(children) < children_count:
            first_parent = self._random_choice(parents)
            second_parent = self._random_choice(parents)

            first_child, second_child = self._cross_individuals(
                first_parent, second_parent
            )

            children.append(first_child)
            children.append(second_child)

        return children

    def _mutate_children(self, children: list[Individual]) -> None:
        for individual in children:
            for i in range(len(individual)):
                chance = self._random_chance()
                if chance < self._mutation_rate:
                    individual[i] = self._random_gene()

    def _consolidate_population(
        self, children: list[Individual], elite: list[Individual]
    ) -> None:
        self._population = children

        self._population.extend(elite)

        self._sort_population()

    def _iterate(self) -> None:
        elite = self._select_elite()

        parents = self._select_parents()

        children = self._cross_parents(parents, len(self._population) - len(elite))

        self._mutate_children(children)

        self._consolidate_population(children, elite)

    def get_individual(self, at: float) -> tuple[str, int]:
        position = round((len(self._population) - 1) * at)
        individual = self._population[position]

        return self._individual_to_str(individual), self._fit_individual(individual)

    def run(self, callback: Callable[[int, GeneticAlgorithm], None] | None) -> None:
        iterations = 1
        cur = -1
        while cur != 0:
            self._iterate()
            iterations += 1

            if callback is not None:
                callback(iterations, self)

            cur = self._fit_individual(self._population[0])


def main() -> None:
    print("Digite uma frase: ", end="")
    target = input().strip()

    genetic_algorithm = GeneticAlgorithm(target, random=Random(67))

    iterations: list[int] = []
    worse: list[int] = []
    mid: list[int] = []
    best: list[int] = []

    def callback(iteration: int, genetic_algorithm: GeneticAlgorithm) -> None:
        print(f"\nGeração: {iteration}")
        iterations.append(iteration)

        individual, fit = genetic_algorithm.get_individual(1)
        print(f"Pior:   {individual}, com distância {fit}")
        worse.append(fit)

        individual, fit = genetic_algorithm.get_individual(0.5)
        print(f"Médio:  {individual}, com distância {fit}")
        mid.append(fit)

        individual, fit = genetic_algorithm.get_individual(0)
        print(f"Melhor: {individual}, com distância {fit}")
        best.append(fit)

        time.sleep(0.05)

    genetic_algorithm.run(callback)

    plt.title(f'Convergence for "{target}"')
    plt.plot(iterations, worse, label="Worse")
    plt.plot(iterations, mid, label="Mid")
    plt.plot(iterations, best, label="Best")
    plt.legend()
    plt.savefig("./convergence.png")


if __name__ == "__main__":
    main()
