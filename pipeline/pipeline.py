class Pipeline:
    def __init__(self):
        self.components = []
        self.output = None

    def add_component(self, component):
        self.components.append(component)

    def get_component_status(self, component_name):
        for component in self.components:
            if component.name == component_name:
                return component.status
        return "Component not found"

    def run(self, start_component=None):
        for component in self.components:
            if start_component is not None and component.name != start_component:
                component.status = "Skipped"
                print(f"Skipping {component.name}")
                continue

            component.status = "Running"
            print(f"Running {component.name}")

            self.ouput = component.process()
            component.status = "Completed"
            print(f"Completed {component.name}")

        return component.status


