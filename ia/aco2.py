from random import Random
from typing import Any


class AntColonyOptimization:
    def __init__(self) -> None:
        self._random = Random(67)

        self._alpha = 1.0
        self._beta = 2.0
        self._rho = 0.2
        self._n_cities = 20
        self._n_ants = self._n_cities
        self._tolerance = self._n_cities

        self._pheromone = self._init_pheromone()
        self._cities = self._init_cities()
        self._tours = self._init_tours()
        self._q = self._init_q()

    def _print_matrix(self, matrix: list[list[Any]]) -> None:
        text = ""
        for a in matrix:
            for b in a:
                text += f"\t{b}"
            text += "\n"

        print(text, end="")

    def _init_pheromone(self) -> list[list[float]]:
        return [
            [1.0 if i != j else 0 for j in range(self._n_cities)]
            for i in range(self._n_cities)
        ]

    def _init_cities(self) -> list[list[int]]:
        cities = [[0 for _ in range(self._n_cities)] for _ in range(self._n_cities)]

        i = 0
        while i < self._n_cities:
            j = i + 1
            while j < self._n_cities:
                distance = self._random.randint(5, 20)
                cities[i][j] = distance
                cities[j][i] = distance
                j += 1
            i += 1

        return cities

    def _init_tours(self) -> list[list[int]]:
        return [[0 for _ in range(self._n_cities)] for _ in range(self._n_ants)]

    def _init_q(self) -> int:
        tours = [[i for i in range(self._n_cities)] for _ in range(self._n_cities)]
        for tour in tours:
            self._random.shuffle(tour)

        total = 0
        for tour in tours:
            total += self._fit_tour(tour)

        return total // len(tours)

    def _calculate_step_weight(self, current: int, next: int) -> float:
        return (
            self._pheromone[current][next] ** self._alpha
            * (1 / self._cities[current][next]) ** self._beta
        )

    def _random_index(self, proba: list[float]) -> int:
        choice = self._random.random()
        i = 0
        total = proba[i]
        while total < choice:
            i += 1
            total += proba[i]

        return i

    def _select_next_city_index(self, current: int, unvisited: list[int]) -> int:
        weights = [self._calculate_step_weight(current, city) for city in unvisited]
        total = sum(weights)
        weights = [w / total for w in weights]

        next_index = self._random_index(weights)

        return next_index

    def _fit_tour(self, tour: list[int]) -> int:
        total = 0
        for i in range(len(tour)):
            total += self._cities[tour[i]][tour[(i + 1) % len(tour)]]
        return total

    def _evaporate_pheromone(self) -> None:
        for i in range(len(self._pheromone)):
            for j in range(len(self._pheromone[i])):
                self._pheromone[i][j] *= 1.0 - self._rho

    def _walk(self) -> None:
        for i in range(self._n_ants):
            tour = self._tours[i]
            unvisited = [i for i in range(self._n_cities)]
            current = self._random.randint(0, self._n_cities - 1)
            unvisited.pop(current)
            j = 0
            tour[j] = current

            while len(unvisited) > 0:
                next_index = self._select_next_city_index(current, unvisited)
                current = unvisited.pop(next_index)
                j += 1
                tour[j] = current

    def _deposit_pheromone(self, tour: list[int], quantity: float) -> None:
        for i in range(len(tour)):
            self._pheromone[tour[i]][tour[(i + 1) % len(tour)]] += quantity
            self._pheromone[tour[(i + 1) % len(tour)]][tour[i]] += quantity

    def _evaluate(self) -> None:
        fits = [self._fit_tour(tour) for tour in self._tours]

        self._evaporate_pheromone()

        for i, tour in enumerate(self._tours):
            deposit = self._q / fits[i]
            self._deposit_pheromone(tour, deposit)

        self._tours = [z[1] for z in sorted(zip(fits, self._tours), key=lambda z: z[0])]

    def execute(self) -> list[int]:
        print(f"For average random walk: {self._q}")

        global_best_tour = [i for i in range(self._n_cities)]
        global_best_fit = float("inf")
        rounds = 0
        i = 0
        while rounds < self._tolerance:
            self._walk()
            self._evaluate()
            rounds += 1

            walk_best_tour = self._tours[0]
            walk_best_fit = self._fit_tour(walk_best_tour)
            if walk_best_fit < global_best_fit:
                global_best_tour = walk_best_tour.copy()
                global_best_fit = walk_best_fit
                rounds = 0

            print(
                f"Genearation: {i + 1} | Walk Best: ({walk_best_fit}) | Global Best: ({global_best_fit})"
            )
            i += 1

        return global_best_tour


if __name__ == "__main__":
    aco = AntColonyOptimization()
    aco.execute()
