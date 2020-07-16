import random

from mod_loader import mod_loader


@mod_loader.load_func('dragon/is_valid')  # Просто пример регистрации функции, ничего важного на этом этапе
def dragon_is_valid():
    print('dragon is_valid?')
    return random.choice((True, False, False, False))
