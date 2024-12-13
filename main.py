import os
import tarfile
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import csv
import configparser


class VirtualFileSystem:
    def __init__(self, tar_path):
        self.tar_path = tar_path
        self.tar = tarfile.open(tar_path, 'r')
        self.current_dir = '/bs'
        self.file_tree = self.build_file_tree()

    def build_file_tree(self):
        file_tree = {}
        for member in self.tar.getmembers():
            path_parts = member.name.strip('/').split('/')
            current = file_tree
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            if member.isdir():
                current[path_parts[-1]] = {}
            else:
                current[path_parts[-1]] = member
        return file_tree

    def list_dir(self, path):
        node = self.get_node(path)
        if node is not None and isinstance(node, dict):
            dirs = [item + '/' for item in node if isinstance(node[item], dict)]
            files = [item for item in node if not isinstance(node[item], dict)]
            return dirs, files
        return [], []

    def change_dir(self, path):
        if path == "/":
            self.current_dir = "/bs"
            return

        parts = path.split('/')
        if path.startswith('/'):
            new_dir = ["bs"]
        else:
            new_dir = self.current_dir.strip('/').split('/')

        for part in parts:
            if part == "..":
                if len(new_dir) > 1:
                    new_dir.pop()
            elif part == "." or part == "":
                continue
            else:
                new_dir.append(part)

        full_path = "/" + "/".join(new_dir).strip('/')
        if self.get_node(full_path) is not None:
            self.current_dir = full_path
        else:
            raise FileNotFoundError(f"cd: no such file or directory: {path}")

    def get_node(self, path):
        parts = path.strip("/").split('/')
        current = self.file_tree
        for part in parts:
            if part and part in current:
                current = current[part]
            else:
                return None
        return current

    def read_file(self, path):
        full_path = os.path.join(self.current_dir, path).replace("\\", "/").strip('/')
        node = self.get_node(full_path)

        if isinstance(node, tarfile.TarInfo) and node.isfile():
            file_obj = self.tar.extractfile(node)
            if file_obj:
                try:
                    return file_obj.read().decode('utf-8')
                except UnicodeDecodeError:
                    raise ValueError(f"File '{path}' contains binary data and cannot be read as text")
            else:
                raise FileNotFoundError(f"Cannot extract file '{path}' from archive")
        raise FileNotFoundError(f"Cannot read file '{path}': No such file or it is not a regular file")

    def copy(self, source, destination):
        source_path = os.path.join(self.current_dir, source).replace("\\", "/").strip('/')
        src_node = self.get_node(source_path)

        if src_node is None:
            raise FileNotFoundError(f"cp: cannot copy '{source}': No such file or directory")

        if destination.startswith('/'):
            dest_path = destination.strip('/')
        else:
            dest_path = os.path.join(self.current_dir, destination).replace("\\", "/").strip('/')

        dest_parts = dest_path.split('/')
        dest_dir = "/".join(dest_parts[:-1])
        dest_name = dest_parts[-1]

        dest_dir_node = self.get_node(dest_dir) if dest_dir else self.file_tree
        if dest_dir and dest_dir_node is None:
            raise FileNotFoundError(f"cp: cannot copy to '{destination}': Directory does not exist")

        if isinstance(src_node, tarfile.TarInfo) and src_node.isfile():
            if dest_dir:
                dest_dir_node[dest_name] = src_node
            else:
                self.file_tree[dest_name] = src_node
        elif isinstance(src_node, dict):
            def recursive_copy(src, dest):
                for name, node in src.items():
                    if isinstance(node, dict):
                        dest[name] = {}
                        recursive_copy(node, dest[name])
                    else:
                        dest[name] = node

            if dest_dir:
                dest_dir_node[dest_name] = {}
                recursive_copy(src_node, dest_dir_node[dest_name])
            else:
                self.file_tree[dest_name] = {}
                recursive_copy(src_node, self.file_tree[dest_name])

    def tac(self, path):
        """Вывод содержимого файла в обратном порядке строк."""
        full_path = os.path.join(self.current_dir, path).replace("\\", "/").strip('/')
        node = self.get_node(full_path)
        if isinstance(node, tarfile.TarInfo) and node.isfile():
            file_obj = self.tar.extractfile(node)
            if file_obj:
                try:
                    content = file_obj.read().decode('utf-8')
                    return "\n".join(reversed(content.splitlines()))
                except UnicodeDecodeError:
                    raise ValueError(f"File '{path}' contains binary data and cannot be read as text")
            else:
                raise FileNotFoundError(f"Cannot extract file '{path}' from archive")
        raise FileNotFoundError(f"Cannot read file '{path}': No such file or it is not a regular file")

    def chmod(self, mode, path):
        """Эмуляция изменения прав доступа к файлу."""
        full_path = os.path.join(self.current_dir, path).replace("\\", "/").strip('/')
        node = self.get_node(full_path)
        if node is None:
            raise FileNotFoundError(f"chmod: cannot access '{path}': No such file or directory")

        if isinstance(node, tarfile.TarInfo):
            # Эмулируем изменение прав доступа, добавляя атрибут mode.
            if not hasattr(node, 'mode'):
                node.mode = mode
            else:
                node.mode = mode
        else:
            raise ValueError(f"chmod: '{path}' is not a regular file or directory")

class ShellEmulator:
    def __init__(self, root, config, vfs):
        self.root = root
        self.root.title("Shell Emulator by Balasova V.V.")
        self.username = config['User']
        self.hostname = config['Host']
        self.vfs = vfs
        self.log_file = config['Log']
        self.output = scrolledtext.ScrolledText(root, height=20, width=60, state=tk.DISABLED, bg="white", fg="black")
        self.output.pack()

        self.input = tk.Entry(root, width=80)
        self.input.pack()
        self.input.bind("<Return>", self.run_command)

        self.init_log()
        self.update_prompt()

    def init_log(self):
        # Создать CSV-файл с заголовками, если он ещё не существует
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'user', 'command'])

    def log_action(self, command):
        # Добавить новую строку в CSV
        with open(self.log_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), self.username, command])

    def execute_startup_script(self, script_path):
        if script_path and os.path.exists(script_path):
            with open(script_path, 'r') as script:
                for line in script:
                    self.execute_command(line.strip())

    def update_prompt(self):
        prompt = f"{self.username}@{self.hostname}:{self.vfs.current_dir.replace('/bs', '~')}$ "
        self.input.delete(0, tk.END)
        self.input.insert(0, prompt)
        self.input.icursor(len(prompt))

    def run_command(self, event):
        command = self.input.get().split('$', 1)[-1].strip()
        self.log_action(command)
        self.execute_command(command)
        self.update_prompt()

    def execute_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd, *args = parts
        if cmd == "ls":
            self.ls()
        elif cmd == "cd":
            self.cd(args[0] if args else "/")
        elif cmd == "cp":
            if len(args) < 2:
                self.write_output("cp: missing destination file operand after source\n")
            else:
                self.cp(args[0], args[1])
        elif cmd == "tac":
            if len(args) < 1:
                self.write_output("tac: missing file operand\n")
            else:
                self.tac(args[0])
        elif cmd == "chmod":
            if len(args) < 2:
                self.write_output("chmod: missing operand\n")
            else:
                self.chmod(args[0], args[1])
        elif cmd == "exit":
            self.write_output("Program exited\n")
            import sys
            sys.exit(0)
        else:
            self.write_output(f"{cmd}: command not found\n")

    def ls(self):
        dirs, files = self.vfs.list_dir(self.vfs.current_dir)
        self.write_output("\n".join(dirs + files) + "\n")

    def cd(self, path):
        try:
            self.vfs.change_dir(path)
            self.write_output(f"Directory changed to {self.vfs.current_dir.replace('/bs', '~')}\n")
        except FileNotFoundError:
            self.write_output(f"cd: {path}: No such file or directory\n")

    def cp(self, source, destination):
        try:
            self.vfs.copy(source, destination)
            self.write_output(f"Copied {source} to {destination}\n")
        except FileNotFoundError:
            self.write_output(f"cp: cannot copy '{source}': No such file or directory\n")

    def tac(self, path):
        try:
            reversed_content = self.vfs.tac(path)
            self.write_output(reversed_content + "\n")
        except FileNotFoundError:
            self.write_output(f"tac: cannot open '{path}': No such file or directory\n")
        except ValueError as e:
            self.write_output(str(e) + "\n")

    def chmod(self, mode, path):
        try:
            self.vfs.chmod(mode, path)
            self.write_output(f"Changed mode of {path} to {mode}\n")
        except FileNotFoundError:
            self.write_output(f"chmod: cannot access '{path}': No such file or directory\n")
        except ValueError as e:
            self.write_output(str(e) + "\n")

    def write_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini',  encoding='utf-8')

    vfs = VirtualFileSystem(config['Settings']['VFS'])
    root = tk.Tk()
    shell = ShellEmulator(root, config['Settings'], vfs)
    root.mainloop()


if __name__ == "__main__":
    main()