import subprocess
import os
from ..utils.style_console_text import red, green, blue, bold, reset
from .functions import (
    create_build_directories, article_names, articles_dir_path, portfolio_names, portfolios_dir_path, build_message, get_build_directory, get_name_of_latex_main_file
)
from .parameters import (
    articles_directory,
    portfolios_directory,
    build_folder__aux_files,
    build_folder__main_output,
)
from .recipes import recipe__biber, recipe__full, recipe__lualatex
from ..enums.BuildMode import BuildMode
import argparse
from datetime import datetime


def perform_build_steps(args: argparse.Namespace):
    """Compile a LaTeX document (article or portfolio) with lualaTeX.

    Args:
        args (argparse.Namespace): namespace with arguments parsed via command line.
    """

    build_directory = get_build_directory(args)
    latex_doc_name = get_name_of_latex_main_file(args)

    try:
        # print( os.path.join(dir_path, thing_name + ".tex"))
        # CHANGE DIRECTORY TO THING'S
        os.chdir(build_directory)
        # CREATE BUILD FOLDERS IF IT DOES NOT EXIST
        create_build_directories()

        print(f"\n🏗️ BUILD MODE: {blue}{args.mode}{reset}\n")
        match args.mode:
            case BuildMode.full.value :
                recipe__full(args, latex_doc_name)
            case BuildMode.lualatex.value:
                recipe__lualatex(args, latex_doc_name)
            case BuildMode.biber.value :
                recipe__biber(args, latex_doc_name)
            case _:
                print(f"{red}CHOSEN COMPILATION MODE ({args.mode}) DOES NOT EXIST {reset}")
                exit()

        print(f"\n✅ {green}Compilation in {bold}{args.mode}{reset}{green} mode finished for {bold}{args.thing_name}{reset} \n")

    except subprocess.CalledProcessError as e:
        print("Compilation log:")
        print(e.stdout)
        print(e.stderr)
        print(f"{red}Compilation failed{reset}")
