class Queue:

    def __init__(self):

        self.queue = []

    

    def enqueue(self, data):

        self.queue.append(data)

    

    def dequeue(self, data):

        data = None

        try:
            data = self.queue.pop(0)
        except IndexError as ex:
            pass

        return data

    

    def is_empty(self):

        return len(self.queue) == 0