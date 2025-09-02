class NavigationService:
    def __init__(self, stack, modules, state_manager):
        self.stack = stack
        self.modules = modules
        self.state = state_manager

    def navigate_to(self, module_name):
        if module_name in self.modules:
            self.stack.setCurrentWidget(self.modules[module_name])
            self.state.set_module(module_name)
            