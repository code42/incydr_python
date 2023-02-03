try:
    from _incydr_cli.main import incydr
except ModuleNotFoundError:
    err_message = (
        "Missing CLI dependencies. To use Incydr CLI run: pip install 'incydr[cli]'"
    )
    import sys

    if "--python" in sys.argv:
        print(sys.executable)
    else:
        print(
            "Missing CLI dependencies. To use Incydr CLI run: pip install 'incydr[cli]'"
        )
    exit(1)

incydr()
