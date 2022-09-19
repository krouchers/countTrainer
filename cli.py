"""
Commandline interface.
"""
import sys
import time
import os
import argparse
from pathlib import Path
from decimal import Decimal, InvalidOperation

sys.path.insert(0, str(Path(__file__).parent))
from core import Arithmetictrainer
from core import create_arithmetictrainer_from_files
from __init__ import version

def parse_args():
    """Parse commandline arguments"""
    parser = argparse.ArgumentParser(
        prog="Arithmetictrainer",
        description="Train mental arithmetic",
    )
    parser.add_argument(
            '-n',
            '--number',
            type=int,
            default=10,
            help='Number of tasks to solve'
    )
    parser.add_argument(
            '-c', '--config', type=str, help='Path to configuration file'
    )
    parser.add_argument(
            '--version', action='version', version=f'%(prog)s {version}'
    )
    parser.add_argument(
            '-w', '--web', action='store_true',
            help='Open run simple http server accessible on localhost:8000')
    parser.add_argument(
            '-p', '--port', help='Only used when "--web" is present',
            type=int, default=8000)
    return parser.parse_args()

def get_config(args) -> Path:
    if args.config and Path(args.config).is_file():
        config = Path(args.config)
    elif Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')
        ).joinpath('arithmetictrainer/config').is_file():
        config = Path(
                os.environ.get('XDG_CONFIG_HOME', '~/.config')
                ).joinpath('arithmetictrainer/config')
    elif Path.cwd().joinpath('config').is_file():
        config = Path.cwd().joinpath('config')
    else:
        config = Path(__file__).parent.joinpath('data/config'),
    return config

def get_answer(task: dict) -> Decimal:
    """
    Get an answer for *task*. Raises KeyboardInterrupt if user input is one
    of ('q', 'quit', (exit')
    """
    print('Round to ' + str(task['result_decimal_points']) + ' decimal points')
    numeric_answer = False
    while not numeric_answer:
        answer = input(task['task'] + ' = ').strip()
        if answer in ('q', 'quit', 'exit'):
            raise KeyboardInterrupt
        try:
            answer = Decimal(answer)
            numeric_answer = True
        except InvalidOperation:
            answer = False
            numeric_answer = False
    return answer


def main():
    args = parse_args()
    config = get_config(args)
    trainer = create_arithmetictrainer_from_files(config)
    if args.web:
        import webgui
        webgui.main(trainer, port=args.port)
    while trainer.getState()['num_correct_answers'] < args.number:
        try:
            answer = get_answer(trainer.getTask())
            was_correct = trainer.answer(answer)
            if was_correct:
                print('*' * 3)
        except KeyboardInterrupt:
            break
    stats = trainer.getState()
    print()
    print('*' * 10)
    print('Solved', stats['num_correct_answers'], 'tasks')
    print('in', stats['seconds_since_started'],'seconds.')
    print(f'With', stats['num_incorrect_answers'], 'incorrect answers')
    print('*' * 10)


if __name__ == '__main__':
    main()
