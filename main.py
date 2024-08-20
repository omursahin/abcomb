from ABC import ABC

if __name__ == "__main__":
    runtime = 30
    test_lengths = []
    for i in range(runtime):
        t_strength = 2
        number_of_parameter = 3
        number_of_possible_value = 3

        abc_algorithm = ABC(t_strength, number_of_parameter, number_of_possible_value)
        tests = abc_algorithm.run()
        test_lengths.append(len(tests))

    print("Mean test length: ", sum(test_lengths) / runtime)
    print("Best test length: ", min(test_lengths))
