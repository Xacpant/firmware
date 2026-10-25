#!/usr/bin/env python3
"""Install this Xacpant project's build dependencies in an isolated local environment."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

TARGET = 'lilygo-t-embed-cc1101-plus'
PLATFORMIO_VERSION = '6.2.0'
PROJECT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='Compile the Plus firmware after installing dependencies')
    parser.add_argument('--plan', action='store_true', help='Show the operations without installing or building')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10 or newer is required')
    if not (PROJECT / 'platformio.ini').is_file():
        parser.error('Keep this script in the tools folder of the extracted Xacpant project')

    tools_dir = PROJECT / '.build-tools'
    environment_dir = tools_dir / 'venv'
    python = environment_dir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    commands = [
        [str(python), '-m', 'pip', 'install', '--disable-pip-version-check', f'platformio=={PLATFORMIO_VERSION}'],
        [str(python), '-m', 'platformio', 'pkg', 'install', '--project-dir', str(PROJECT), '--environment', TARGET],
    ]
    if args.build:
        commands.append([str(python), '-m', 'platformio', 'run', '--project-dir', str(PROJECT), '--environment', TARGET])
    print(f'Project: {PROJECT}', flush=True)
    print(f'Target: {TARGET}', flush=True)
    if args.plan:
        print(f'Create/reuse Python environment: {environment_dir}')
        for command in commands:
            print(subprocess.list2cmdline(command))
        return 0

    if not python.is_file():
        print('Creating isolated Python build environment...', flush=True)
        venv.EnvBuilder(with_pip=True).create(environment_dir)
    process_env = os.environ.copy()
    # Build scripts also invoke the pio entry point by name.
    process_env['PATH'] = str(python.parent) + os.pathsep + process_env.get('PATH', '')
    process_env['PLATFORMIO_CORE_DIR'] = str(tools_dir / 'platformio')
    if os.name == 'nt':
        # Per-process Git setting only; no global Git or Windows settings change.
        config_index = int(process_env.get('GIT_CONFIG_COUNT', '0'))
        process_env[f'GIT_CONFIG_KEY_{config_index}'] = 'core.longpaths'
        process_env[f'GIT_CONFIG_VALUE_{config_index}'] = 'true'
        process_env['GIT_CONFIG_COUNT'] = str(config_index + 1)
    for command in commands:
        subprocess.run(command, check=True, cwd=PROJECT, env=process_env)
    print('Project dependencies installed.' if not args.build else 'Plus firmware build completed.', flush=True)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f'Build setup stopped: command returned {error.returncode}. See the error above.', file=sys.stderr)
        raise SystemExit(error.returncode)
    except OSError as error:
        # OSError covers missing Python/venv binaries and filesystem failures.
        print(f'Build setup failed: {error}', file=sys.stderr)
        raise SystemExit(1)
