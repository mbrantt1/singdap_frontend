from src.components.activo_dialog import ActivoDialog

DIALOG_REGISTRY = {
    "ActivoDialog": ActivoDialog,
}

def get_dialog_class(name: str):
    return DIALOG_REGISTRY.get(name)
