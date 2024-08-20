from TTupleSearch import TTupleSearch
import random
import numpy as np


class ABC:
    def __init__(self, t_strength, number_of_parameter, number_of_possible_value):
        self.t_strength = t_strength
        self.number_of_parameter = number_of_parameter
        self.number_of_possible_value = number_of_possible_value
        self.UPPER_BOUND = number_of_possible_value - 1

        self.LOWER_BOUND = 0
        self.DIMENSION = number_of_parameter
        self.FOOD_NUMBER = 10
        self.LIMIT = 10
        self.MAXIMUM_EVALUATION = 1000

        self.foods = np.zeros((self.FOOD_NUMBER, self.DIMENSION))
        self.f = np.zeros(self.FOOD_NUMBER)
        self.trial = np.zeros(self.FOOD_NUMBER)
        self.prob = [0 for x in range(self.FOOD_NUMBER)]
        self.solution = np.zeros(self.DIMENSION)
        self.globalParams = [0 for x in range(self.DIMENSION)]
        self.globalTime = 0
        self.evalCount = 0
        self.cycle = 0
        self.experimentID = 0
        self.globalOpt = 0
        self.globalOpts = list()

        self.t_tuple = TTupleSearch(t_strength, number_of_possible_value, number_of_parameter)

    def init(self, index):
        self.foods[index] = self.t_tuple.generate_random_solution()
        solution = np.copy(self.foods[index][:])
        fitness = self.calculate_function(solution)
        if fitness == 1:
            self.evalCount = self.MAXIMUM_EVALUATION  # terminate the search
            self.t_tuple.add_test_case(solution)
            solution = np.copy(solution)
            self.smart_search(solution)
            self.foods[index] = self.t_tuple.generate_random_solution()
            solution = np.copy(self.foods[index][:])
            fitness = self.calculate_function(solution)
        self.f[index] = fitness
        self.trial[index] = 0

    def initial(self):
        self.foods = np.zeros((self.FOOD_NUMBER, self.DIMENSION))
        self.f = np.zeros(self.FOOD_NUMBER)
        self.trial = np.zeros(self.FOOD_NUMBER)
        self.prob = [0 for x in range(self.FOOD_NUMBER)]
        self.solution = np.zeros(self.DIMENSION)
        self.globalParams = [0 for x in range(self.DIMENSION)]
        self.globalTime = 0
        self.evalCount = 0
        self.cycle = 0
        self.experimentID = 0
        self.globalOpt = 0
        self.globalOpts = list()

        for i in range(self.FOOD_NUMBER):
            self.init(i)
        self.globalOpt = np.copy(self.f[0])
        self.globalParams = np.copy(self.foods[0][:])

    def smart_search(self, solution):
        for i in range(self.number_of_possible_value - 1):
            solution = [(x + 1) % self.number_of_possible_value for x in solution]
            fitness = self.calculate_function(solution)
            if fitness == 1:
                self.t_tuple.add_test_case(solution)

    def calculate_function(self, sol):
        self.evalCount += 1
        return self.t_tuple.get_fitness_value(sol)

    def calculate_neighbour_solution(self, change_indice):
        r = random.random()
        param2change = (int)(r * self.DIMENSION)

        r = random.random()
        neighbour = (int)(r * self.FOOD_NUMBER)
        while neighbour == change_indice:
            r = random.random()
            neighbour = (int)(r * self.FOOD_NUMBER)
        solution = np.copy(self.foods[change_indice][:])
        r = random.random()
        solution[param2change] = round(self.foods[change_indice][param2change] + (
                self.foods[change_indice][param2change] - self.foods[neighbour][param2change]) * (
                                               r - 0.5) * 2)
        if solution[param2change] < self.LOWER_BOUND:
            solution[param2change] = self.LOWER_BOUND
        if solution[param2change] > self.UPPER_BOUND:
            solution[param2change] = self.UPPER_BOUND
        return solution

    def crossover_solution(self, change_indice):
        solution = np.copy(self.foods[change_indice][:])
        divide_indice = random.randint(1, self.DIMENSION - 2)
        neighbour = random.randint(0, self.FOOD_NUMBER - 1)
        while neighbour == change_indice:
            neighbour = random.randint(0, self.FOOD_NUMBER - 1)
        neighbour_solution = np.copy(self.foods[neighbour][:])
        sol_1 = np.concatenate((solution[:divide_indice], neighbour_solution[divide_indice:]), axis=None)
        sol_2 = np.concatenate((neighbour_solution[:divide_indice], solution[divide_indice:]), axis=None)
        if self.calculate_function(sol_1) > self.calculate_function(sol_2):
            return sol_1
        else:
            return sol_2

    def send_employed_bees(self):
        i = 0
        while i < self.FOOD_NUMBER and self.evalCount < self.MAXIMUM_EVALUATION:
            # solution = self.calculate_neighbour_solution(i)
            solution = self.crossover_solution(i)
            objval_sol = self.calculate_function(solution)
            if objval_sol >= self.f[i]:
                self.trial[i] = 0
                self.foods[i][:] = np.copy(solution)
                self.f[i] = objval_sol
            else:
                self.trial[i] = self.trial[i] + 1
            i += 1

    def calculate_probabilities(self):
        maxfit = np.copy(max(self.f))
        for i in range(self.FOOD_NUMBER):
            self.prob[i] = (0.9 * (self.f[i] / maxfit)) + 0.1

    def send_onlooker_bees(self):
        i = 0
        t = 0
        while t < self.FOOD_NUMBER and self.evalCount < self.MAXIMUM_EVALUATION:
            r = random.random()
            if r > self.prob[i]:
                t += 1

                # solution = self.calculate_neighbour_solution(i)
                solution = self.crossover_solution(i)

                objval_sol = self.calculate_function(solution)

                if objval_sol >= self.f[i]:
                    self.trial[i] = 0
                    self.foods[i][:] = np.copy(solution)
                    self.f[i] = objval_sol
                else:
                    self.trial[i] = self.trial[i] + 1
            i += 1
            i = i % self.FOOD_NUMBER

    def send_scout_bees(self):
        if np.amax(self.trial) >= self.LIMIT:
            self.init(self.trial.argmax(axis=0))

    def increase_cycle(self):
        self.cycle += 1

    def stopping_condition(self):
        status = bool(self.evalCount >= self.MAXIMUM_EVALUATION)
        return status

    def memorize_best_source(self):
        best_source = max(self.f)
        if best_source > self.globalOpt:
            self.globalOpt = best_source
            self.globalParams = self.foods[self.f.argmax(axis=0)]

    def run(self):
        while self.t_tuple.get_coverage() < 1:
            self.initial()
            self.memorize_best_source()
            while not self.stopping_condition():
                self.send_employed_bees()
                self.send_onlooker_bees()
                self.send_scout_bees()
                self.memorize_best_source()
            self.t_tuple.add_test_case(self.globalParams)
        unique_test_cases = self.t_tuple.get_unique_test_cases()
        print("Length of unique test cases: ", len(unique_test_cases))

        return unique_test_cases
