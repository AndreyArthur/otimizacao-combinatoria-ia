from random import Random
import sys


def initialize_population(
    random: Random, target: list[int], size: int
) -> list[list[int]]:
    population: list[list[int]] = []
    for _ in range(size):
        instance: list[int] = []
        for _ in range(len(target)):
            instance.append(random.randint(ord("A"), ord("z")))

        population.append(instance)

    return population


def fit_instance(target: list[int], instance: list[int]) -> int:
    sum = 0

    for index, value in enumerate(instance):
        diff = value - target[index]

        sum += diff * diff

    return sum


def sort_population(target: list[int], population: list[list[int]]) -> list[list[int]]:
    return sorted(
        population, key=lambda instance: fit_instance(target, instance), reverse=True
    )


def print_instance(target: list[int], instance: list[int]) -> None:
    text = ""
    for code in instance:
        text += chr(code)
    print(f"{text}, fit: {fit_instance(target, instance)}")


def russian_roulette(
    random: Random, target: list[int], population: list[list[int]]
) -> tuple[list[list[int]], list[int]]:
    ratings: list[float] = [1.0 / float(fit_instance(target, x)) for x in population]
    ratings_sum = sum(ratings)

    for index, value in enumerate(ratings):
        ratings[index] = value / ratings_sum

    r = random.random()
    s = -0.0

    i = 0
    while s < r:
        s += ratings[i]
        if s >= r:
            break
        i += 1

    out = population[i]

    return population, out


def select_elite(
    population: list[list[int]], full_len: int, rate: float
) -> tuple[list[list[int]], list[list[int]]]:
    to_cut = int(round(rate * full_len))
    cut_index = len(population) - to_cut

    return population[:cut_index], population[cut_index:]


def select_parents(
    random: Random,
    target: list[int],
    population: list[list[int]],
    full_len: int,
    rate: float,
) -> tuple[list[list[int]], list[list[int]]]:
    to_cut = int(round(rate * full_len))
    if to_cut % 2 != 0:
        to_cut = to_cut - 1 if to_cut > 0 else to_cut + 1

    parents: list[list[int]] = []
    current = population

    while len(parents) < to_cut:
        current, parent = russian_roulette(random, target, population)
        parents.append(parent)

    return current, parents


def select_next(
    random: Random,
    parents: list[list[int]],
    quantity: int,
    crossover_rate: float,
    mutation_rate: float,
) -> list[list[int]]:
    parents_copy = parents.copy()

    children: list[list[int]] = []

    while len(children) < quantity:
        if len(parents_copy) <= 0:
            parents_copy = parents.copy()

        candidate1 = parents_copy.pop(random.randint(0, len(parents_copy) - 1))
        candidate2 = parents_copy.pop(random.randint(0, len(parents_copy) - 1))
        children1: list[int] = []
        children2: list[int] = []

        r = random.random()
        cut = random.randint(0, len(candidate1) + 1)

        if r < crossover_rate:
            children1 = candidate1[cut:]
            children1.extend(candidate2[:cut])
            children2 = candidate2[cut:]
            children2.extend(candidate1[:cut])
        else:
            children1 = candidate1
            children2 = candidate2

        for i in range(len(children1)):
            r = random.random()
            if r < mutation_rate:
                children1[i] = random.randint(ord("A"), ord("z"))

            r = random.random()
            if r < mutation_rate:
                children2[i] = random.randint(ord("A"), ord("z"))

        children.append(children1)
        children.append(children2)

    return children


def loop(
    random: Random,
    target: list[int],
    population: list[list[int]],
    elitism_rate: float,
    selection_rate: float,
    crossover_rate: float,
    mutation_rate: float,
) -> list[list[int]]:
    current = population
    full_len = len(current)

    _, elite = select_elite(current, full_len, elitism_rate)

    _, parents = select_parents(random, target, current, full_len, selection_rate)

    current = select_next(
        random, parents, full_len - len(elite), crossover_rate, mutation_rate
    )

    current.extend(elite)

    current = sort_population(target, current)

    return current


if __name__ == "__main__":
    MAX_INT, MIN_INT = sys.maxsize, -sys.maxsize - 1

    random = Random(67)

    target = [ord(x) for x in "EuAdoroInteligenciaArtificialPorqueTemMuitaMatematica"]
    population_size = len(target) * 2

    population = initialize_population(random, target, population_size)
    population = sort_population(target, population)

    current = population
    count = 0
    while True:
        instance = current[len(current) // 4]
        print_instance(target, instance)

        instance = current[len(current) // 2]
        print_instance(target, instance)

        instance = current[len(current) - 1]
        print_instance(target, instance)

        end = True
        for index, value in enumerate(instance):
            if value != target[index]:
                end = False

        if end:
            print(f"at {count + 1} generation")
            break

        current = loop(random, target, current, 4 / population_size, 0.96, 0.80, 0.03)
        count += 1
