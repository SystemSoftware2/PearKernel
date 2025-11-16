# TerminalOS.py - эмулятор терминала на моём ядре. Ядро нужно закачать в папку где будет этот файл

import re
import time
from kernel import *

class VFS:
    def __init__(self):
        self.files = {
            '/etc/version': 'TerminalOS 0.1',
            '/home/user/README.txt': 'Welcome to TerminalOS!\nType "help" for commands.',
        }
        self.dirs = {'/', '/etc', '/home', '/home/user'}

    def ls(self, path):
        if path not in self.dirs:
            return f'ls: cannot access \'{path}\': No such directory'
        contents = []
        for p in self.files:
            if p.startswith(path) and p != path:
                rel = p[len(path):].lstrip('/')
                if '/' not in rel or rel.split('/')[0] == '':
                    contents.append(rel.split('/')[0])
        for d in self.dirs:
            if d.startswith(path) and d != path:
                rel = d[len(path):].lstrip('/')
                if '/' not in rel:
                    contents.append(rel + '/')
        return '\n'.join(sorted(set(contents))) if contents else ''

    def cat(self, path):
        return self.files.get(path, f'cat: {path}: No such file')

    def write(self, path, data):
        self.files[path] = data
        parts = path.strip('/').split('/')
        for i in range(1, len(parts)):
            self.dirs.add('/' + '/'.join(parts[:i]))

    def mkdir(self, path):
        if path in self.dirs:
            return f'mkdir: cannot create directory \'{path}\': File exists'
        self.dirs.add(path)
        return ''

class Terminal:
    def __init__(self, kernel, vfs):
        self.kernel = kernel
        self.vfs = vfs
        self.cwd = '/home/user'
        self.prompt = 'user@terminalos:~$ '

    def resolve_path(self, path):
        if path == '.':
            return self.cwd
        if path == '..':
            return '/'.join(self.cwd.strip('/').split('/')[:-1]) or '/'
        if path.startswith('/'):
            return path
        return self.cwd + '/' + path

    def execute(self, cmd_line):
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ''

        parts = re.split(r'\s+', cmd_line)
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == 'help':
            return '''Available commands:
  help           - show this help
  ls [DIR]     - list directory contents
  cd [DIR]     - change directory
  pwd          - print working directory
  cat FILE     - display file content
  echo TEXT > FILE - write text to file
  echo TEXT - show text to terminal
  mkdir DIR    - create directory
  version      - show OS version
  exit         - shut down'''

        elif cmd == 'ls':
            path = self.resolve_path(args[0] if args else self.cwd)
            return self.vfs.ls(path)

        elif cmd == 'cd':
            path = self.resolve_path(args[0] if args else '/')
            if path in self.vfs.dirs:
                self.cwd = path
                self.prompt = f'user@terminalos:{self.cwd}$ '
            else:
                return f'cd: {args[0]}: No such directory'

        elif cmd == 'pwd':
            return self.cwd

        elif cmd == 'cat':
            if not args:
                return 'cat: missing file operand'
            path = self.resolve_path(args[0])
            return self.vfs.cat(path)

        elif cmd.startswith('echo') and '>' in cmd_line:
            match = re.match(r'echo\s+(.*?)\s+>\s+(\S+)', cmd_line)
            if match:
                text, file_path = match.groups()
                path = self.resolve_path(file_path)
                self.vfs.write(path, text)
                return ''
            else:
                return 'echo: syntax error. Use: echo TEXT > FILE'

        elif cmd.startswith('echo'):
            if not args:
                return 'echo: missing file operand'
            return ' '.join(args[0:])

        elif cmd == 'mkdir':
            if not args:
                return 'mkdir: missing operand'
            path = self.resolve_path(args[0])
            return self.vfs.mkdir(path)

        elif cmd == 'version':
            return self.vfs.cat('/etc/version')

        elif cmd == 'exit':
            return 'Shutting down...'

        else:
            return f'{cmd}: command not found'

def terminal_task(kernel, pid):
    terminal = kernel.terminal
    print('TerminalOS 0.1 — Type "help" for commands.')
    while True:
        try:
            cmd = input(terminal.prompt)
            output = terminal.execute(cmd)
            if cmd.strip().lower() == 'exit':
                print('Shutting down...')
                break
            elif output:
                print(output)
        except (EOFError, KeyboardInterrupt):
            print('Shutting down...')
            break

def main():
    kernel = Kernel()
    vfs = VFS()
    terminal = Terminal(kernel, vfs)

    kernel.terminal = terminal

    kernel.create_task(1, terminal_task, priority=0)

    kernel.run_loop()

if __name__ == '__main__':
    main()

