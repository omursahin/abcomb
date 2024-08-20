from itertools import combinations, product
from math import comb

import numpy as np


class TTupleSearch:
    def __init__(self, t_strength, number_of_possible_value, number_of_parameter):
        self.__targets = []
        self.t_strength = t_strength
        self.number_of_possible_value = number_of_possible_value
        self.number_of_parameter = number_of_parameter
        # self.__possible_max_value = len(np.array(list(combinations(self.number_of_parameter * [0], self.t_strength))))
        self.__possible_max_value = comb(number_of_parameter, t_strength) * number_of_possible_value ** t_strength
        len(np.array(list(combinations(self.number_of_parameter * [0], self.t_strength))))

        items = range(0, number_of_parameter)  # 2^3'deki 3'ye karşılık gelir, eleman sayısı. 2^3 derken de 3 farklı
        # eleman 2 farklı değer alır demek.
        unique_parameters = np.array(list(combinations(items, t_strength)))
        val = range(0, number_of_possible_value)  # 2^3'deki 2'ye karşılık gelir, kaç farklı değer alır?
        possible_values = np.array(list(product(val, repeat=t_strength)))
        # T-Tuple Array oluşturma
        self.__t_tuple = np.empty((0, number_of_parameter), int)
        for i in unique_parameters:
            for j in possible_values:
                init_value = np.array([-1] * number_of_parameter)
                np.put(init_value, i, j)
                self.__t_tuple = np.vstack((self.__t_tuple, init_value))
                self.__targets.append(Target(init_value))

        self.__unique_test_cases = []

    def generate_possible_solutions(self, solution):
        possible_solutions = np.empty((0, len(solution)), int)
        solution_comb_indices = np.array(list(combinations(enumerate(solution), self.t_strength)))
        for sol in solution_comb_indices:
            indices = sol[:, 0].astype(int)
            values = sol[:, 1]
            init_value = np.array([-1.] * self.number_of_parameter)
            np.put(init_value, indices, values)
            possible_solutions = np.vstack((possible_solutions, init_value))
        return possible_solutions

    def get_t_tuple(self):
        return self.__t_tuple

    def get_possible_max_value(self):
        return self.__possible_max_value

    def get_targets(self, not_covered=False):
        if not_covered:
            return [x for x in self.__targets if not x.is_covered]
        return self.__targets

    def get_unique_test_cases(self):
        return self.__unique_test_cases

    def get_fitness_value_old(self, test_case):
        test_cases = self.generate_possible_solutions(test_case)
        covered_targets = []
        for tc in test_cases:
            found = [x for x in self.get_targets(not_covered=True) if np.array_equal(x.goal, np.array(tc))]
            if not len(found) == 0:
                covered_targets.append(found[0])
        return len(covered_targets) / self.__possible_max_value

    def get_fitness_value(self, test_case):
        test_cases = self.generate_possible_solutions(test_case)
        goals = [g.goal for g in self.get_targets(not_covered=True)]
        covered_targets = [tc for tc in test_cases if not np.argwhere((goals == tc).all(axis=1)).__len__() == 0]
        return covered_targets.__len__() / self.__possible_max_value

    def add_test_case(self, test_case):
        test_cases = self.generate_possible_solutions(test_case)
        covered_targets = []
        already_covered = []
        for tc in test_cases:
            found = [x for x in self.__targets if np.array_equal(x.goal, np.array(tc))]
            if found[0].is_covered:
                already_covered.append(found[0])
            else:
                covered_targets.append(found[0])
        fitness_value = len(covered_targets)
        tc_obj = TestCase(test_case, fitness_value, covered_targets, already_covered)
        for tc in test_cases:
            found = [x for x in self.__targets if np.array_equal(x.goal, np.array(tc))]
            for f in found:
                f.test_cases.append(tc_obj)
                f.is_covered = True
        if fitness_value > 0:
            self.__unique_test_cases.append(tc_obj)
        return tc_obj

    def get_uncovered_targets(self):
        return [x for x in self.__targets if not x.is_covered]

    def get_covered_targets(self):
        return [x for x in self.__targets if x.is_covered]

    def get_coverage(self):
        return len(self.get_covered_targets()) / len(self.__targets)

    def generate_random_solution(self):
        return np.random.randint(0, self.number_of_possible_value, self.number_of_parameter)


class Target:
    def __init__(self, goal):
        self.goal = goal
        self.test_cases = []
        self.is_covered = False


class TestCase:
    def __init__(self, test_case, fitness_value, covered_targets, already_covered):
        self.test_case = test_case
        self.fitness_value = fitness_value
        self.covered_targets = covered_targets
        self.already_covered = already_covered
