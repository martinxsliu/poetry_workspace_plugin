import random
import time


def main():
    print("running liba")


def main_slow():
    print("started liba")
    slow("liba")
    print("finished liba")


def slow(name: str):
    n = random.randint(1, 5)
    for i in range(n):
        time.sleep(1)
        print(f"{name}: {i+1}/{n}")
