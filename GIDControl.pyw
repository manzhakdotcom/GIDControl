# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import *
import configparser
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


class Config:
    def __init__(self):
        self.file = 'settings.ini'

    def is_file(self, file):
        if not os.path.exists(file):
            return False
        else:
            return True

    def create_config_file(self, config):
        config['Settings'] = { 'path': 'c:\\неман\\System\\Log\\',
                                'file': 'PArchGraf.log',
                                      }
        with open(self.file, "w", encoding='utf-8') as config_file:
            config.write(config_file)
        return config

    def get_data(self, config):
        config.read(self.file, encoding='utf-8')
        data = {}
        for section in config.sections():
            data[section] = {}
            for (key, val) in config.items(section):
                data[section][key] = val
        return data

    def options(self):
        config = configparser.ConfigParser()
        if self.is_file(self.file):
            return self.get_data(config)
        else:
            MsgBox = messagebox.askquestion('Создать файл', 'Файл '
                                            + self.file
                                            + ' отсуствует. Создать файл с примером настроек?',
                                            icon='warning')
            if MsgBox == 'yes':
                self.create_config_file(config)
                messagebox.showinfo('Сообщение', 'Файл '
                                    + self.file
                                    + ' создан. Настройте его и запустите программу.')
                sys.exit(1)
            elif MsgBox == 'no':
                messagebox.showinfo('Сообщение', 'Без файла '
                                    + self.file
                                    + ' с настройками программа работать не будет.')
                sys.exit(1)


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        settings = Config().options()
        if settings['Settings']['file'] in event.src_path:
            with open(settings['Settings']['path']+settings['Settings']['file'], 'r') as file:
                line = file.readlines()[-1]
                if settings['Settings']['key'] in line:
                    messagebox.showerror('Ошибка', 'Программа Архиватор ГИД выключена. Обратитесь к инженеру КТЦ для восстановления его работы.')


class Control:
    def __init__(self):
        path = sys.argv[1] if len(sys.argv) > 1 else self.get_path(Config().options())
        event_handler = MyHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)

    def get_path(self, data):
        path = data['Settings']['path']
        return path

    def start(self):
        self.observer.start()
        print('Start')
        while getattr(threading.currentThread(), "do_run", True):
            time.sleep(1)
        else:
            self.stop()
        self.observer.join()

    def stop(self):
        self.observer.stop()
        print('Stop')


class App:
    def __init__(self, root):
        self.root = root
        self.root.bind('<F1>', self.top_level_about)
        self.root.bind('<Control-q>', self.close)
        self.root.bind('<Control-r>', self.run)
        self.menu()
        self.elements()

    def menu(self):
        self.root.option_add('*tearOff', False)
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file = Menu(menubar)
        about = Menu(menubar)

        menubar.add_cascade(menu=file, label='Файл')
        menubar.add_cascade(menu=about, label='?')

        file.add_command(label='Запустить', command=self.run, accelerator="Ctrl+R")
        file.add_separator()
        file.add_command(label='Выйти', command=self.close, accelerator="Ctrl+Q")

        about.add_command(label='О программе', command=self.top_level_about, accelerator="F1")

    def close(self, event=None):
        self.control.do_run = False
        self.control.join()
        self.root.destroy()

    def elements(self):
        self.frame = Frame(self.root)
        self.frame.pack(ipady=20)
        self.btn_start = Button(self.frame, text='Запустить', command=self.run)
        self.btn_stop = Button(self.frame, text='Остоновить', command=self.stop, state='disabled')
        self.btn_start.pack(ipadx=20, ipady=10, side=LEFT)
        self.btn_stop.pack(ipadx=20, ipady=10, side=LEFT)

    def refresh(self):
        self.root.update()
        self.root.after(1000, self.refresh)

    def run(self, event=None):
        self.refresh()
        self.control = threading.Thread(target=Control().start)
        self.control.start()
        self.btn_start['state'] = 'disabled'
        self.btn_stop['state'] = 'normal'
        self.btn_start.update()
        self.btn_stop.update()

    def stop(self, event=None):
        self.refresh()
        self.control.do_run = False
        self.control.join()
        self.btn_start['state'] = 'normal'
        self.btn_stop['state'] = 'disabled'
        self.btn_start.update()
        self.btn_stop.update()

    def top_level_about(self, event=None):
        win = Toplevel(self.root)
        win.resizable(0, 0)
        center(win, 220, 120, 0)
        win.iconbitmap(os.getcwd() + os.path.sep + 'icon.ico')
        win.title('О программе')

        frame = Frame(win)
        frame.pack()

        label1 = Label(frame, text='Программа контролирует\nфайл PArchGraf.log на наличие\nзаписи "Закрытие программы".')
        label2 = Label(frame, text='Автор © Манжак С.С.')
        label3 = Label(frame, text='Версия v' + self.root.version + ' Win 32')

        label1.grid(row=0, column=0, pady=10)
        label2.grid(row=1, column=0)
        label3.grid(row=2, column=0)

        win.focus_set()
        win.grab_set()
        win.wait_window()


def center(root, width, height, offset):
    x = round(root.winfo_screenwidth() / 2 - width / 2 + offset)
    y = round(root.winfo_screenheight() / 2 - height / 2 + offset)
    root.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))


def main():
    root = Tk()
    root.version = '0.0.1'
    root.resizable(0, 0)
    center(root, 280, 120, 0)
    root.title('ГИД контроль')
    root.iconbitmap(os.getcwd() + os.path.sep + 'icon.ico')
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == '__main__':
    main()
