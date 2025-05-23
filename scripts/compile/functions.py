
import os
import argparse
from datetime import datetime
from scripts.utils.helpers import list_existing_things 
import scripts.utils.style_console_text as sty
from scripts.enums.ThingType import ThingType
import enum
from scripts.compile.parameters import (
    articles_directory,
    portfolios_directory,
    build_folder__aux_files,
    build_folder__main_output,
)
from scripts.enums.Recipe import Recipe
from typing import Optional

# get the directory of the current script
base_dir = os.path.dirname(os.path.realpath(__file__))  # dir of current file
articles_dir_path = os.path.join(base_dir, articles_directory)
portfolios_dir_path = os.path.join(base_dir, portfolios_directory)

article_names = list_existing_things(articles_dir_path, print_list=False)
portfolio_names = list_existing_things(portfolios_dir_path, print_list=False)
thing_names = article_names + portfolio_names



def list_as_string(list: list[any], sep:str=", ") -> str:
    """create a string out of a python list.

    Args:
        list (list[any]): list from which to create a string
        sep (str, optional): Separator between list items. Defaults to ", ".

    Returns:
        str: A string made out of the list items.
    """
    return sep.join([f"{sty.blue}{e}{sty.reset}" for e in list])


def enum_list_as_string(enumName: enum.Enum, sep:str=", ") -> str:
    """create a string out of a python Enum.

    Args:
        enumName (enum.Enum): Enum from which to create a string
        sep (str, optional): Separator between Enum items. Defaults to ", ".

    Returns:
        str: A sring made out of the Enum options.
    """
    return sep.join([f"{sty.blue}{e.value}{sty.reset}" for e in enumName])


article_list_as_string = list_as_string(article_names)
portfolio_list_as_string = list_as_string(article_names)
thing_name_list_as_string = list_as_string(thing_names)
thing_type_list_as_string = enum_list_as_string(ThingType)


def deal_with_user_input(args__cmd_line: argparse.Namespace) -> argparse.Namespace:
    """Manage user arguments passed through the command line, and collect missing ones through the input() command.
    Additionally, perform tests for availability, quit commands and index inputs.

    Args:
        args__cmd_line (argparse.Namespace): user passed arguments through the command line

    Returns:
        argparse.Namespace: Validated and updated arguments
    """

    # If something has been provided in the command line as first argument but it is the build recipe:
    if args__cmd_line.thing_name in [e.value for e in Recipe]:
        # Pass it to the right arg and empty the thing_name arg
        args__cmd_line.recipe = args__cmd_line.thing_name
        args__cmd_line.thing_name = None


    # get and test user input thing (target document) as passed through the command line; may be empty in which case input is collected with the input() command
    thing_name_from_cmd_line = args__cmd_line.thing_name

    keep_asking = True
    while keep_asking == True:
        # If no thing name has been provided in the command line directly, request it from the user
        if thing_name_from_cmd_line == None:
            art_names = list_existing_things(
                articles_dir_path, header_message="Articles:"
            )
            prt_names = list_existing_things(
                portfolios_dir_path,
                header_message="Portfolio versions:",
                cnt_start=len(art_names),
            )
            all_names = art_names + prt_names
            indexes = list(range(1, len(all_names) + 1))
            choice = input(
                f"Which do you want to compile? ({sty.blue}choose from options above{sty.reset}): "
            )
            #  if user passed an instruction to quit the program:
            if choice in ["q", "quit"]:
                print(f"\n💀💀💀 {sty.red}Program quit without compiling anything.{sty.reset}")
                exit()
            # if user picked a valid index (number):
            elif choice.isdigit() and int(choice) in indexes:
                thing_name = all_names[int(choice) - 1]
            # if user wrote the article name directly and it is valid:
            elif choice in thing_names:
                thing_name = choice
            # if invalid choice (non existing name or index):
            else:
                print(f"\n\n\n{sty.red}Invalid choice{sty.reset}, pick from options:\n")
                continue

            args__cmd_line.thing_name = thing_name
            print_choice_mesg(args__cmd_line)
            keep_asking = False

        # If thing name has been provided...
        # ...but it does not actually exist:
        elif thing_name_from_cmd_line not in thing_names:
            print(f"\n\n\n{sty.red}thing_name{sty.reset} does not exist, pick from options:\n")
            # Restart proccess
            thing_name = None
        # ...and it exists:
        else:
            # Exit loop
            args__cmd_line.thing_name = thing_name_from_cmd_line
            print_choice_mesg(args__cmd_line)
            keep_asking = False

    return args__cmd_line


def print_choice_mesg(args:argparse.Namespace) -> None:
    """print a string announcing the document chosen by the user.

    Args:
        args (argparse.Namespace): an argument namespace.
    """
    print(f"You have chosen to compile {sty.blue}{args.thing_name}{sty.reset} in {sty.blue}{args.recipe}{sty.reset} recipe\n...")



def get_build_directory(args: argparse.Namespace) -> str:
    """ determine directory where to perform build

    Args:
        args (argparse.Namespace): arguments passed by the user

    Returns:
        str: path to build directory
    """
    if args.thing_name in article_names:
        dir_path = articles_dir_path
    elif args.thing_name in portfolio_names:
        dir_path = portfolios_dir_path
    build_directory = os.path.join(dir_path, args.thing_name)
    return build_directory



def get_name_of_latex_main_file(args: argparse.Namespace) -> str:
    """ determine name of latex .tex main file to be compiled.

    Args:
        args (argparse.Namespace): arguments passed by the user

    Returns:
        str: name of latex main file
    """
    if args.thing_name in article_names:
        return  "document"
    elif args.thing_name in portfolio_names:
        return "portfolio_document"





def create_build_directories() -> None:
    """
    Create required build directories if they do not exist yet
    """
    if not os.path.exists(build_folder__main_output):
        os.makedirs(build_folder__main_output)
    if not os.path.exists(build_folder__aux_files):
        os.makedirs(build_folder__aux_files)


def build_message(msg: str, counter: int,time_start : datetime, time_prev: Optional[datetime] = None, isTimer: bool = True) -> datetime:
    """Print message reporting the compilation progress.

    Args:
        msg (str): Message to be printed to console.
        counter (int): A counter to be incremented with each call of the function.
        time_start (datetime): Time corresponding to the beginning of the compilation process (T0)
        time_prev (datetime | None, optional): Time corresponding to the previous compilation step (Tn-1). Defaults to None.
        isTimer (bool, optional): Whether to print the messages or only increment the counter. Defaults to True.

    Returns:
        datetime: _description_
    """
    counter+=1
    print(f"{sty.blue}{msg}{sty.reset} (step {counter})")
    if isTimer:
        time_now = datetime.now()
        delta_start = time_now - time_start
        print(f"\t⏲ {'Elapsed time since beginning:':<30} {sty.green}{round(delta_start.total_seconds(), 2)}{sty.reset} seconds")
        if time_prev != None:
            delta_prev = time_now - time_prev
            print(f"\t⏲ {'Elapsed time since prev. step:':<30} {sty.green}{round(delta_prev.total_seconds(), 2)}{sty.reset} seconds")
        return (time_now, counter)
    return (None, counter)