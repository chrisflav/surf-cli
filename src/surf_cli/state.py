"""Global CLI state shared across commands."""


class _State:
    verbose: bool = False


state = _State()
