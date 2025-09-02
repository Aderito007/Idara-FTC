def load_cargos(departamento):
    data = load_all()
    cargos = data.get("cargos", {})
    return cargos.get(departamento, [])

def add_cargo(departamento, cargo):
    cargo = cargo.strip()
    if not cargo:
        return False
    data = load_all()
    cargos = data.get("cargos", {})
    lista = cargos.get(departamento, [])
    if cargo not in lista:
        lista.append(cargo)
        cargos[departamento] = lista
        data["cargos"] = cargos
        save_all(data)
        return True
    return False

def remove_cargo(departamento, cargo):
    data = load_all()
    cargos = data.get("cargos", {})
    lista = cargos.get(departamento, [])
    if cargo in lista:
        lista.remove(cargo)
        cargos[departamento] = lista
        data["cargos"] = cargos
        save_all(data)
        return True
    return False
import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'combo_data.json')

DEFAULTS = {
    "departamentos": ["RH", "TI", "Financeiro"],
    "cargos": {
        "RH": ["Analista", "Assistente"],
        "TI": ["Desenvolvedor", "Suporte"],
        "Financeiro": ["Contador", "Analista Financeiro"]
    }
}

def load_items(key):
    if not os.path.exists(DATA_FILE):
        save_all(DEFAULTS)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get(key, [])

def add_item(key, value):
    value = value.strip()
    if not value:
        return False
    data = load_all()
    items = data.get(key, [])
    if value not in items:
        items.append(value)
        data[key] = items
        save_all(data)
        return True
    return False

def remove_item(key, value):
    data = load_all()
    items = data.get(key, [])
    if value in items:
        items.remove(value)
        data[key] = items
        save_all(data)
        return True
    return False

def load_all():
    if not os.path.exists(DATA_FILE):
        save_all(DEFAULTS)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_all(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
