# PearKernel
Небольшое ядро для твоей небольшой ОС на MicroPython.

# Функции ядра
send_mes(pid, mes) - отправить сообщение на pid (int или str).

take_mes(pid, index=0) - даст сообщение с tasks[pid].mailbox и удалить его.

run_task(pid) - запустить задачу с pid (int или str).

scheduler() - вам это не нужно. Планирует по приоритету.

run_loop() - запустить все задачи.

close_task() - вам это не нужно но это закрывает задачу (она сама закрывается).

set_priority(pid, priority) - поменять приоритет у tasks[pid] (чем меньше тем оно запустится первее).

# Пример задач

Вот код:

```py
from kernel import *

def sender(kernel, pid):
    kernel.send_mes(2, input("exp>"))
    
def receiver(kernel, pid):
    print(eval(kernel.take_mes(pid)))
    
kernel = Kernel()

kernel.create_task(1, sender, 0)
kernel.create_task(2, receiver, 1)

kernel.run_loop(4)
````

Ну, как работает это легко понять (надеюсь).
