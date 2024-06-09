from typing import Callable
from dataclasses import dataclass


@dataclass
class Option:
    name: str
    func: Callable
    args: any = None


def prompt_input(prompt: str):
    return input(f"{prompt} > ")


def prompt_number(prompt: str, min: int, max: int):
    try:
        number = int(prompt_input(prompt))
        if number < min or number > max:
            raise ValueError
        return number
    except ValueError:
        print("Invalid input.")
        return prompt_number(prompt, max, min)


def prompt_selection(size: int):
    return prompt_number("Select", 0, size - 1)


def show_menu(title, options: list[Option]):
    print(f"\n{title}")
    for i, option in enumerate(options):
        print(f"{i}. {option.name}")
    print(f"{len(options)}. Exit")
    selection = prompt_selection(len(options) + 1)
    print()

    if selection == len(options):
        return True

    option = options[selection]
    return option.func(option.args)


def show_menu_loop(title, options: list[Option]):
    while not show_menu(title, options):
        continue
