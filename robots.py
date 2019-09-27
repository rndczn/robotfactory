import random
from collections import defaultdict as ddict

from tabulate import tabulate

ROBOT_MONEY_PRICE = 3
ROBOT_FOO_PRICE = 6
MAX_FOOBAR_SELL = 5
FOOBAR_PRICE = 1

VERBOSE = 3

TARGET = 30

class Product:
    def __repr__(self):
        return ''.join(c for c in str(self.__class__.__name__) if c.isupper()) + '#' + str(self.id)


class Foo(Product):
    _count = 0

    def __init__(self):
        self.id = Foo._count
        Foo._count += 1


class Bar(Product):
    _count = 0

    def __init__(self):
        self.id = Foo._count
        Bar._count += 1


class FooBar(Product):
    def __init__(self, foo, bar):
        self.id = str(foo.id) + '_' + str(bar.id)


class Robot:
    _count = 0

    _COSTS = {
        'idle': 0,
        'mine_foo': 1,
        'mine_bar': 2,
        'make_foobar': 2,
        'sell_foobar': 10,
        'buy_robot': 1
    }

    def __init__(self):
        self.id = Robot._count
        Robot._count += 1

        self.bars = []
        self.foos = []
        self.foobars = []
        self.money = 0

        self.activity = 'idle'
        self.time_remaining = 0

    def __repr__(self):
        return 'R#' + str(self.id).ljust(len(str(Robot._count)))

    def set_activity(self, activity):
        if activity != self.activity:
            self.time_remaining += 5
        self.activity = activity
        self.time_remaining += Robot._COSTS[activity]

    def idle(self):
        if VERBOSE > 2:
            print(self, 'does nothing')

    def mine_foo(self):
        self.foos.append(Foo())
        if VERBOSE > 2:
            print(self, 'mines', self.foos[-1])

    def mine_bar(self):
        time = Robot._COSTS['mine_bar']
        while time >= 0:
            self.bars.append(Bar())
            if VERBOSE > 2:
                print(self, 'mines', self.bars[-1])

            time -= random.uniform(.5, 2)

    def make_foobar(self):
        foo = self.foos.pop()
        if random.random() <= .6:
            bar = self.bars.pop()
            self.foobars.append(FooBar(foo, bar))
            if VERBOSE > 2:
                print(self, 'makes', self.foobars[-1])

    def sell_foobar(self):
        money = 0
        while money < 5 * FOOBAR_PRICE and self.foobars:
            money += FOOBAR_PRICE
            fb = self.foobars.pop()
            if VERBOSE > 2:
                print(self, 'sells', fb)
        self.money += money

    def buy_robot(self):
        robots = []
        while self.money >= ROBOT_MONEY_PRICE and len(self.foos) >= ROBOT_FOO_PRICE:
            for _ in range(ROBOT_FOO_PRICE): self.foos.pop()
            self.money -= ROBOT_MONEY_PRICE
            robots.append(Robot())
            if VERBOSE > 2:
                print(self, 'buys ', robots[-1])
        return robots


class Factory:
    def __init__(self):
        self.bars = []
        self.foos = []
        self.foobars = []
        self.money = 0

        self.robots = []

    def print_status(self):
        if VERBOSE:
            self.print_resources()
            if VERBOSE > 1:
                self.print_robots()

    def print_resources(self):
        cols = ['foos', 'bars', 'foobars', 'robots', 'money']
        table = [[len(self.foos), len(self.bars), len(self.foobars), len(self.robots), self.money]]
        print()
        print(' Resources '.center(50, '-'))
        print(tabulate(table, cols, tablefmt='fancy_grid'))

    def print_robots(self):
        cols = ['id', 'foos', 'bars', 'foobars', 'money', 'activity', 'time_remaining']
        table = [[getattr(robot, col) for col in cols] for robot in self.robots]
        print()
        print(' Robots '.center(50, '-'))
        print(tabulate(table, cols, tablefmt='fancy_grid'))

    def _collect(self, robot):
        self.foos.extend(robot.foos)
        robot.foos = []
        self.bars.extend(robot.bars)
        robot.bars = []
        self.foobars.extend(robot.foobars)
        robot.foobars = []
        self.money += robot.money
        robot.money = 0

    def _select_available_robot(self, available_robots):
        if available_robots['idle']:
            return available_robots['idle'].pop()
        elif available_robots['buy_robot']:
            return available_robots['buy_robot'].pop()
        elif available_robots['sell_foobar']:
            return available_robots['sell_foobar'].pop()
        elif available_robots['make_foobar']:
            return available_robots['make_foobar'].pop()
        elif available_robots['mine_bar']:
            return available_robots['mine_bar'].pop()
        else:
            return available_robots['mine_foo'].pop()

    def _schedule(self):
        available_robots = ddict(list)

        for robot in self.robots:
            if robot.time_remaining <= 0:
                available_robots[robot.activity].append(robot)

        while any(robots for robots in available_robots.values()):
            robot = self._select_available_robot(available_robots)

            # buy robots
            buyable_robots = min(self.money // ROBOT_MONEY_PRICE, len(self.foos) // ROBOT_FOO_PRICE)
            if buyable_robots:
                robot.money += buyable_robots * ROBOT_MONEY_PRICE
                self.money -= buyable_robots * ROBOT_MONEY_PRICE
                while len(robot.foos) < buyable_robots * ROBOT_FOO_PRICE:
                    robot.foos.append(self.foos.pop())
                robot.set_activity('buy_robot')
                continue

            # sell foobars
            if len(self.foobars) >= 5:
                while len(robot.foobars) < 5:
                    robot.foobars.append(self.foobars.pop())
                robot.set_activity('sell_foobar')
                continue

            # make foobars
            if len(self.foos) > 5 - len(self.foobars) and len(self.bars) > 5 - len(self.foobars):
                robot.foos.append(self.foos.pop())
                robot.bars.append(self.bars.pop())
                robot.set_activity('make_foobar')
                continue

            # mine bar
            bar_miners = sum(1 for robot in self.robots if robot.activity == 'mine_bar')
            foo_miners = sum(1 for robot in self.robots if robot.activity == 'mine_foo')

            if 2 * len(self.bars) <= len(self.foos) and bar_miners < foo_miners:
                robot.set_activity('mine_bar')
                continue

            # mine foo
            robot.set_activity('mine_foo')

    def turn(self):
        if VERBOSE > 2:
            print()
            print(' Actions '.center(50,'-'))
        for robot in self.robots:
            robot.time_remaining -= 1
            if robot.time_remaining == 0:
                if robot.activity == 'buy_robot':
                    self.robots.extend(getattr(robot, robot.activity)())
                else:
                    getattr(robot, robot.activity)()
                    self._collect(robot)

        self.print_status()

        self._schedule()


if __name__ == '__main__':
    factory = Factory()
    factory.robots.append(Robot())
    factory.robots.append(Robot())

    factory.print_status()

    turn = 0
    while len(factory.robots) < TARGET:
        print()
        print((' Turn ' + str(turn) + ' ').center(100, '='))
        factory.turn()
        turn += 1
