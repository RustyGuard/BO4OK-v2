import random

from mod_loader import mod_loader


@mod_loader.load_func('warrior/is_valid')  # Просто пример регистрации функции, ничего важного на этом этапе
def mine_is_valid():
    print('is_valid?')
    return random.choice((True, False))
