from mod_loader import mod_loader


@mod_loader.load_func('warrior/is_valid')
def warrior_is_valid(self, unit):
    return unit.team != self.team


@mod_loader.load_func('archer/is_valid')
def archer_is_valid(self, unit):
    return unit.team != self.team


@mod_loader.load_func('warrior/when_close')
def warrior_when_close(self):
    self.single_attack()


@mod_loader.load_func('archer/when_close')
def archer_when_close(self):
    self.throw_projectile('arrow')

