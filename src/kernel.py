#micropython не знает о существовании модуля "logging" (и это плохо)

class Logger:
  
    """
    Класс для логгера.
    Вообще это типо называют костылём.

    :error: (mes: str, name (опционально): str)
    :debug: (mes: str, name (опционально): str)
    :warning: (mes: str, name (опционально): str)
    """
  
    def __init__(self):
        pass

    def error(self, mes, name="KERNEL"):
        print(f'[{name}]: [Error]: {mes}')

    def debug(self, mes, name="KERNEL"):
        print(f'[{name}]: {mes}')

    def warning(self, mes, name="KERNEL"):
        print(f'[{name}]:: [Warning]: {mes}')

"""
Статусы для задач.

RUNNING: запущено.
CLOSED: выключено.
ALREADY_RAN: уже было запущено

Статус ALREADY_RAN нужен для правильной работы функции "schedule" (см. дальше)
"""

RUNNING = "RUNNING"
CLOSED = "CLOSED"
ALREADY_RAN = "ALREADY_RAN"

class Task:

    """
    Задача для ядра.

    Параметры:
    :pid: int (но можно str)
    :func: функция с параметрами kernel и pid
    :priority: (необязательно) int
    """
  
    def __init__(self, pid, func, priority=0):
        self.pid = pid
        self.func = func
        self.priority = priority
        self.state = CLOSED
        self.mailbox = []

class Kernel:
    #будет прокомментировано)
    def __init__(self):
        self.tasks = {}
        self.logger = Logger()
        self.ready_queue = []

    def create_task(self, pid, func, priority=0):
        if pid in self.tasks:
            self.logger.error(f'PID {pid} already exists.')
            return False
        proc = Task(pid, func, priority)
        self.tasks[pid] = proc
        self.logger.debug(f'New task created. PID: {pid}, Priority: {priority}')

    def send_mes(self, pid, mes):
        if pid not in self.tasks:
            self.logger.error(f"I don't know this PID: {pid}")
            return False
        self.tasks[pid].mailbox.append(mes)
        self.logger.debug(f'Message sended to PID {pid}: {mes}')

    def take_mes(self, pid, index=0):
        if pid not in self.tasks:
            self.logger.error(f"I don't know this PID: {pid}")
            return None
        if not self.tasks[pid].mailbox:
            self.logger.warning(f'No messages in mailbox for PID {pid}')
            return None
        if index < 0 or index >= len(self.tasks[pid].mailbox):
            self.logger.error(f'Invalid index {index} for mailbox of PID {pid}')
            return None
        mes = self.tasks[pid].mailbox[index]
        del self.tasks[pid].mailbox[index]
        return mes

    def run_task(self, pid):
        if pid not in self.tasks:
            self.logger.error(f"I don't know this PID: {pid}")
            return False
        elif self.tasks[pid].state == ALREADY_RAN:
            self.logger.error(f'Task PID {pid} already ran and cannot be restarted.')
            return False
        try:
            self.tasks[pid].state = RUNNING
            self.logger.debug(f'Running task PID {pid}')
            self.tasks[pid].func(self, pid)
            self.close_task(pid)
        except Exception as e:
            self.logger.error(f'Task with PID {pid} crashed: {e}')

    def schedule(self):
        self.ready_queue = [
            pid for pid, task in self.tasks.items()
            if task.state == CLOSED
        ]
        self.ready_queue.sort(key=lambda pid: self.tasks[pid].priority)
        if not self.ready_queue:
            self.logger.debug('No tasks to schedule.')
            return
        next_pid = self.ready_queue[0]
        self.logger.debug(f'Scheduled task PID {next_pid} (priority: {self.tasks[next_pid].priority})')
        self.run_task(next_pid)
        
    def run_loop(self, iterations=1):
        for q in range(iterations):
            self.logger.debug(f'Running all tasks... ({q + 1}/{iterations})')
            for i in range(len(self.tasks)):
                self.schedule()
            for j in self.tasks.keys():
                self.tasks[j].state = CLOSED
        self.logger.debug('All tasks completed.')

    def close_task(self, pid):
        if pid in self.tasks:
            self.tasks[pid].state = ALREADY_RAN
            self.logger.debug(f'Task PID {pid} closed.')
        else:
            self.logger.error(f"I don't know this PID: {pid}")
            
    def set_priority(self, pid, new_priority):
        if pid in self.tasks:
            self.tasks[pid].priority = new_priority
            self.logger.debug(f'Priority of PID {pid} updated to {new_priority}')
        else:
            self.logger.error(f"Unknown PID: {pid}")
