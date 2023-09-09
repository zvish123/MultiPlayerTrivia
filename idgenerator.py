import random
from threading import Lock, Thread
import time
import threading


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """
    _instances = {}
    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class IdGeneratorSingleton(metaclass=SingletonMeta):
    value: int = 0
    """
    We'll use this property to prove that our Singleton really works.
    """
    def __init__(self, log_name) -> None:
        self.value = 0
        self.log_name = log_name

    def get_next_id(self):
        """
        Finally, any singleton should define some business logic, which can be
        executed on its instance.
        """
        with IdGeneratorSingleton._lock:
            file = open(self.log_name, 'r')
            num = file.read()
            if num != '':
                self.value = int(num) + 1
            else:
                self.value = self.value + 1
            file.close()
            file = open(self.log_name, 'w')
            file.write(str(self.value))
            file.close()
            return self.value


class GameIdGenerator(IdGeneratorSingleton):
    def __init__(self):
        super().__init__("last_game_id.dat")


class PlayerIdGenerator(IdGeneratorSingleton):
    def __init__(self):
        super().__init__("last_player_id.dat")


if __name__ == "__main__":
    # The client code.
    r = random.Random()


    def test_singleton1() -> None:
        time.sleep(r.random() * 10)
        print(f"start singleton on thread {threading.current_thread().name}")
        singleton = GameIdGenerator()
        print(singleton.get_next_id())


    def test_singleton2() -> None:
        time.sleep(r.random() * 10)
        print(f"start singleton on thread {threading.current_thread().name}")
        singleton = PlayerIdGenerator()
        print(singleton.get_next_id())

    print("If you see the same value, then singleton was reused (yay!)\n"
          "If you see different values, "
          "then 2 singletons were created (booo!!)\n\n"
          "RESULT:\n")

    processes = []
    for i in range(5):
        process = Thread(target=test_singleton1)
        processes.append(process)
        process = Thread(target=test_singleton2)
        processes.append(process)

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print("finish")
