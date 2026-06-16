import sys

if "--tui" in sys.argv:
    from .tui import run_tui
    run_tui()
else:
    from .main import run
    run()
