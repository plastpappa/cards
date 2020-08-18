def const(x):
    return lambda *args, **kwargs: x

def id(x):
    return x


do_nothing = const(None)
