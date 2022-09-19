"""
Core objects.
"""
import time
import random
import functools
import decimal
import json
import configparser
from decimal import Decimal, getcontext, InvalidOperation


def get_number(var_min, var_max, decimal_points, allow_zero=False) -> Decimal:
    """
    Get a Decimal in range [var_min, var_max].
    The number is rounded to  variable_decimal_points.
    """
    if var_min >= var_max:
        raise ValueError('"var_min" >= "var_max"')
    if decimal_points < 0:
        raise ValueError('"decimal_points" < 0')
    getcontext().rounding = decimal.ROUND_HALF_UP
    x = random.randint(var_min, var_max) * random.random()
    x = Decimal(x)
    x = round(x, decimal_points)
    while x == Decimal('0') and not allow_zero:
        x = random.randint(var_min, var_max) * random.random()
        x = Decimal(x)
        x = round(x, decimal_points)
    return x

def get_number_array(num_vars, var_min, var_max, decimal_points, allow_zero=False) -> list[Decimal]:
    """
    Get a list with generated Decimal numbers. 
    The numbers are in range [var_min, var_max] and rounded to 
    variable_decimal_points.
    """
    l = []
    for i in range(num_vars):
        l.append(get_number(var_min, var_max, decimal_points, allow_zero=allow_zero))
    return l

class Arithmetictrainer:

    def __init__(self, config: list[dict], current_task=None, state=None):
        """
        current_task:
            A task as returned by the getTask method.
        state:
            A state as returned by the getState method.
        config:
            A config as returned by the getConfig method.
        """
        if len(config) <= 0:
            raise ValueError('Not a valid config')
        if state is None:
            state = {
                    'started_at': time.time(),
                    'num_correct_answers': 0,
                    'num_incorrect_answers': 0,
            }
        self.config = config
        self.state = state
        if current_task is not None:
            self.current_task = current_task
        else:
            next(self)
            

    def getState(self) -> dict:
        """
        Get the state of the Arithmetictrainer. Valid keyes are:

        - started_at: float
        - seconds_since_started: float
        - num_incorrect_answers: str
        - num_correct_answers: str
        """
        self.state['seconds_since_started'] = time.time() - self.state['started_at'] 
        return self.state

    def getConfig(self) -> list[dict]:
        """
        Get the config of Arithmetictrainer. Each dictonary in the
        list contains the following keyes:

        operator: str
            A sign which describes the operator.
        variable_num: int
            The number of variables
        variable_min: int
            The smallest possible variable
        variable_max: int
            The largest possible variable
        variable_decimal_points: int
            The decimal points of each variable
        result_decimal_points: int
            The decimal points the result is rounded to.
        """
        return self.config

    def getTask(self) -> dict:
        """
            Return a dictonary which describe's a task.::

                {
                    'task': str,
                    'result_decimal_points': int,
                    'correct_answer': str,
                }
        """
        return self.current_task


    def answer(self, answer: str | Decimal):
        """
        Answer the current_task. If answer was correct return true, else false
        """
        try:
            answer = Decimal(answer)
        except InvalidOperation:
            answer = None
        if answer == Decimal(self.getTask()['correct_answer']):
            self.state['num_correct_answers'] += 1
            next(self)
            return True
        self.state['num_incorrect_answers'] += 1
        return False

    
    def toJsonSerializable(self):
        """
        Return an object that represents a Arithmetictrainer and can be
        converted to json with for example *json.dumps*.
        """
        return [self.getConfig(), self.getTask(), self.getState()]

    def __next__(self):
        """
        Set and Return the next task
        """
        result = {}
        conf = random.choice(self.config)
        variables = get_number_array(
                conf['variable_num'], 
                conf['variable_min'],
                conf['variable_max'],
                conf['variable_decimal_points'],
        )
        match conf['operator']:
            case '+':
                correct_answer = sum(variables)
            case '-':
                correct_answer = functools.reduce(lambda x, y: x - y, variables)
            case '*':
                correct_answer = functools.reduce(lambda x, y: x * y, variables)
            case '/' | ':':
                correct_answer = functools.reduce(lambda x, y: x / y, variables)
            case _:
                raise ValueError(f'[{conf["operator"]}] is not a valid operator')
        result['correct_answer'] = round(
                correct_answer, conf['variable_decimal_points'])
        result['correct_answer'] = str(result['correct_answer'])
        result['result_decimal_points'] = conf['result_decimal_points']
        result['task'] = functools.reduce(
                lambda x, y: '{} {} {}'.format(x, conf['operator'], y), variables)
        self.current_task = result
        return result

    def __eq__(self, other) -> bool:
        if self.getConfig() != other.getConfig():
            return False
        if self.getTask() != other.getTask():
            return False
        if self.getState()['started_at'] != other.getState()['started_at']:
            return False
        return True



def arithmetictrainerFromJson(json_arithmetictrainer) -> Arithmetictrainer:
    """
    Create an Arithmetictrainer from a Json array as returned by the
    *Arithmetictrainer.toJsonSerializable* method.
    """
    l = json.loads(json_arithmetictrainer)
    return Arithmetictrainer(*l)


def create_arithmetictrainer_from_files(*files) -> Arithmetictrainer:
    """
    Create a Arithmetictrainer from a configuration file.
    """
    config_files = configparser.ConfigParser()
    config_files.read(*files)
    if len(config_files.sections()) == 0:
        raise ValueError("Could not find a valid config in: ", *files)
    config = []
    for section in config_files.sections():
        tmp = {}
        tmp['operator'] = config_files[section]['operator']
        tmp['variable_num'] = config_files.getint(section, 'variable_num')
        tmp['variable_min'] = config_files.getint(section, 'variable_min')
        tmp['variable_max'] = config_files.getint(section, 'variable_max')
        tmp['variable_decimal_points'] = config_files.getint(
                section, 'variable_decimal_points')
        tmp['result_decimal_points'] = config_files.getint(
                section, 'result_decimal_points')
        config.append(tmp)
    return Arithmetictrainer(config)

