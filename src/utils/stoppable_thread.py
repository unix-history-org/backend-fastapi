from threading import Thread


class StoppableThread(Thread):
    def stop(self):
        super()._stop()
