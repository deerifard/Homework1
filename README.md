# Homework1
# Общее описание  
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу 
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС. 
Эмулятор должен запускаться из реальной командной строки, а файл с 
виртуальной файловой системой не нужно распаковывать у пользователя. 
Эмулятор принимает образ виртуальной файловой системы в виде файла формата 
tar. Эмулятор должен работать в режиме GUI.  
Конфигурационный файл имеет формат ini и содержит:  
• Имя пользователя для показа в приглашении к вводу.  
• Имя компьютера для показа в приглашении к вводу.  
• Путь к архиву виртуальной файловой системы.  
• Путь к лог-файлу.  
Лог-файл имеет формат csv и содержит все действия во время последнего 
сеанса работы с эмулятором. Для каждого действия указан пользователь.  
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также 
следующие команды:  
1. tac.  
2. cp.  
3. chmod.  
Все функции эмулятора должны быть покрыты тестами, а для каждой из 
поддерживаемых команд необходимо написать 2 теста.
# Описание всех функций и настроек
### Функциональность программы  
Программа представляет собой эмуляцию оболочки (shell) с функциями работы с виртуальной файловой системой, основанной на архиве .tar.   Основные возможности:

### Виртуальная файловая система:

Навигация по файловой системе: команды ls, cd.  
Чтение содержимого файлов.  
Копирование файлов и папок внутри виртуальной файловой системы.  
Обратный вывод содержимого файла (tac).  
Эмуляция изменения прав доступа (chmod).  

### Логирование:
Логирование всех введённых команд в формате CSV.

### Интерфейс пользователя:
Графический интерфейс на базе tkinter.
Ввод и выполнение команд через текстовый интерфейс с автоподстановкой пути.

# Основные классы и функции

### VirtualFileSystem
Класс для работы с виртуальной файловой системой:  

__init__(tar_path) — инициализация VFS из архива .tar.  
list_dir(path) — возвращает список папок и файлов в указанной директории.  
change_dir(path) — изменяет текущую директорию.  
read_file(path) — читает содержимое файла.  
copy(source, destination) — копирует файлы или папки.  
tac(path) — выводит содержимое файла в обратном порядке.  
chmod(mode, path) — эмулирует изменение прав доступа.  

### ShellEmulator  
Класс для реализации эмуляции shell:  

run_command(event) — обработка введённой команды.  
ls() — отображение содержимого текущей директории.  
cd(path) — смена текущей директории.  
cp(source, destination) — копирование файлов/папок.  
tac(path) — обратный вывод содержимого файла.  
chmod(mode, path) — изменение прав доступа.  
log_action(command) — запись команды в лог.  
write_output(text) — вывод текста в интерфейсе.  

### Примеры использования
![image](https://github.com/user-attachments/assets/fa650f00-9083-471e-8cae-cd868ff58a4f)
