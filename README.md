# robotfactory

## Installation

This project should work with any Python3.5+, I tried to avoid newer features.

The only dependency is *tabulate*

```
pip3 install tabulate
```

## Configuration

The verbosity of the program can be configured via the *VERBOSITY* variable in robots.py :

- 0 : Nothing is printed
- 1 : The factory resources are printed each turn
- 2 : The state of each robot is also printed
- 3 : The robot actions are also printed

## How to run

```
python3 robots.py
```

## Hypothesis

- the robots start doing nothing
- buying a robot takes in fact 1s but you can buy as many robots as you want during a turn
- the bar mining time and the foobar production use uniform probabilities
- for the bar mining we randomly chose the number of bars producted in 2s
