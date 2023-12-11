import abc

class Component(abc.ABC):
    '''Abstract class for a component in a pipeline'''
    def __init__(self, name):
        self.name = name
        self.input_data = None
        self.output_data = None
        self.status = "Not Started"

    @abc.abstractmethod
    def process(self):
        '''Start processing the data'''
        pass

