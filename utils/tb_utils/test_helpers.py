class SigmaDeltaGenerator:
    """True sigma-delta modulator for precise valid rate generation."""

    def __init__(self, valid_rate):
        self.sigma = 100.0
        self.delta = valid_rate * 100.0
        self.accumulator = 0.0

    def set_valid_rate(self, valid_rate):
        self.sigma = 100.0
        self.delta = valid_rate * 100.0
        self.accumulator = 0.0

    def __iter__(self):
        return self

    def __next__(self):
        highs = 0
        lows = 0

        while True:
            self.accumulator += self.delta

            if self.accumulator >= self.sigma:
                highs += 1
                self.accumulator -= self.sigma
                break
            else:
                lows += 1

        return (highs, lows)


def sigma_delta_generator(valid_rate):
    """Generate precise valid/invalid cycles using true sigma-delta modulation."""
    return SigmaDeltaGenerator(valid_rate)


def random_valid_generator():
    """Generate random valid/invalid cycles using random integers."""
    import itertools
    import random

    return ((random.randint(1, 2), random.randint(1, 3)) for _ in itertools.count())


def weighted_random_valid_generator():
    """Generate random valid/invalid cycles with realistic patterns."""
    import random

    def generate():
        while True:
            on_cycles = random.choices([1, 2, 3, 4], weights=[50, 30, 13, 7])[0]
            off_cycles = random.choices([0, 1, 2, 3, 4], weights=[10, 50, 20, 13, 7])[0]
            yield (on_cycles, off_cycles)

    return generate()
