import argparse
import os
import platform

DEFAULT_CONFIG = 'config'
DEFAULT_INTERVAL = 15  # minutes

is_windows = any(platform.win32_ver())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval",
                        help=f'Interval between each execution in minutes (default: {DEFAULT_INTERVAL})',
                        default=DEFAULT_INTERVAL)
    parser.add_argument("-c", "--config", help=f'Path to the configfile to be used (default: {DEFAULT_CONFIG})',
                        default=DEFAULT_CONFIG)
    parser.add_argument("-r", "--replace",
                        help=f'Replace existing cronjobs. WARNING: On linux, this will remove all existing cronjobs for the current user! (default: false)',
                        dest='replace', action='store_true')
    parser.set_defaults(replace=False)
    parser.add_argument('directory')

    args = parser.parse_args()

    create_cronjob(args.directory, args.interval, args.config, args.replace)


def create_cronjob(directory, interval, config, replace):
    if is_windows:
        name = "E2E"
        replace_arg = " /F" if replace else ""
        print(f'Create scheduled task "{name}"')
        os.system(
            f'SchTasks /Create /SC minute /MO {interval} /TN "{name}" /TR "\"{directory}\schedtask_entrypoint.bat\" {config}"{replace_arg}')
        return 0
    else:
        task = f'cd {directory} && behave -t=@monitoring -D config={config}'
        crontab_grep = os.system(f'crontab -l | grep "{task}"')
        if crontab_grep == 0:
            print(f'crontab already exists')
            if replace:
                print(f'delete existing cronjobs')
                os.system(f'crontab -r')
            else:
                return 1

        print(f'create crontab "*/{interval} * * * * {task}"')
        os.system(f'(crontab -l 2>/dev/null; echo "*/{interval} * * * * {task}") | crontab -')
        return 0


if __name__ == "__main__":
    main()
