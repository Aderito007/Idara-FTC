# state_manager.py

class StateManager:
    def __init__(self):
        self.current_module = None
        self.module_states = {}  # Armazena dados específicos por módulo

    def set_module(self, name):
        self.current_module = name

    def get_module(self):
        return self.current_module

    def save_state(self, module_name, state_data):
        """Salva o estado de um módulo (ex: campos, filtros, scroll)"""
        self.module_states[module_name] = state_data

    def get_state(self, module_name):
        """Recupera o estado salvo de um módulo"""
        return self.module_states.get(module_name, {})

    def clear_state(self, module_name):
        """Remove o estado salvo de um módulo"""
        if module_name in self.module_states:
            del self.module_states[module_name]