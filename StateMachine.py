class State:
    def __init__(self, start: callable = lambda: None, update: callable = lambda: None, end: callable = lambda: None):
        self.start = start
        self.update = update
        self.end = end

class StateMachine:
    def __init__(self, startState):
        self.current_state = startState
    
    def change_state(self, newState):
        self.current_state.end()
        self.current_state = newState
        self.current_state.start()
    
    def start(self):
        if self.current_state is not None:
            self.current_state.start()

    def update(self):
        if self.current_state is not None:
            self.current_state.update()