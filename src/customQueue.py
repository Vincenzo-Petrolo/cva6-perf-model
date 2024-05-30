class CustomQueue:
    def __init__(self, max_size):
        self.queue = []
        self.max_size = max_size
    
    def enqueue(self, item):
        if self.full():
            raise OverflowError("enqueue to full queue")
        self.queue.append(item)
    
    def dequeue(self):
        if self.empty():
            raise IndexError("dequeue from empty queue")
        return self.queue.pop(0)
    
    def pop_at(self, index):
        if index < 0 or index >= len(self.queue):
            raise IndexError("index out of range")
        return self.queue.pop(index)
    
    def peek_at(self, index):
        if index < 0 or index >= len(self.queue):
            raise IndexError("index out of range")
        return self.queue[index]
    
    def full(self):
        return len(self.queue) >= self.max_size
    
    def empty(self):
        return len(self.queue) == 0
    
    def __iter__(self):
        return iter(self.queue)
    
    def __len__(self):
        return len(self.queue)
    
    def __str__(self):
        return str(self.queue)
    
    def __getitem__(self, index):
        return self.queue[index]