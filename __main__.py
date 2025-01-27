import sys

from tmi import prompt, cli, log, get_env

if __name__ == "__main__":
    prompt()
    try:
        cli()
    except KeyboardInterrupt:
        print("\n")
        log("info", "Goodbye ...")
    except Exception as main_err:
        log("error", f"{main_err}")
        get_env("", "Press Enter to exit ...")

    sys.exit(0)
