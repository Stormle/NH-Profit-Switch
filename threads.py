from threading import Timer
import asyncio
import time
import threading
import ctypes


class RepeatTimer(Timer):
    def run(self):
        if type(self.args) == "list":
            self.args = tuple(self.args)
        self.function(*self.args, **self.kwargs)
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


async def asyncWithMaxLaps(sleep_time, max_laps, function_to_run, *args):
    """ Use -1 laps for infinite laps or no sleep. Make the function return the string success to break out of laps."""
    if max_laps == 0:
        return
    function_to_run(*args)
    if time != -1:
        await asyncio.sleep(sleep_time)
        await asyncWithMaxLaps(sleep_time, (max_laps - 1, -1)[max_laps == -1], function_to_run, *args)
    else:
        await asyncWithMaxLaps(sleep_time, (max_laps - 1, -1)[max_laps == -1], function_to_run, *args)


class thread_with_exception(threading.Thread):
    def __init__(self, sleep_time, max_laps, function_to_run, args, backup_function, backup_args):
        """ Use -1 laps for infinite laps or no sleep. Make the function return the string success to break out of laps. Backup function runs in case all tries fail."""
        threading.Thread.__init__(self)
        self.sleep_time = sleep_time
        self.max_laps = max_laps
        self.function_to_run = function_to_run
        self.args = args
        self.success = False
        self.backup_function = backup_function
        self.backup_args = backup_args

    def run(self):
        ran_as_long_as_intended = False
        try:
            lap_counter = 0

            if self.max_laps == -1:
                ran_as_long_as_intended = True
            while lap_counter < self.max_laps or self.max_laps == -1:
                if lap_counter + 1 == self.max_laps:
                    ran_as_long_as_intended = True
                ret = ""
                if self.args == "":
                    ret = self.function_to_run()
                else:
                    ret = self.function_to_run(*self.args)
                if ret == "success":
                    self.success = True
                    break
                lap_counter += 1
                if self.sleep_time == -1:
                    continue
                time.sleep(self.sleep_time)
        except (Exception,):
            pass
        finally:
            if ran_as_long_as_intended and not self.success:
                print("Something is wrong. Spinning up the backup.")
                self.backup_function(*self.backup_args)


    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
