from src.components.activo_dialog import ActivoDialog
from src.components.eipd_dialog import EipdDialog

DIALOG_REGISTRY = {
    "ActivoDialog": ActivoDialog,
    "EipdDialog": EipdDialog,
}

def get_dialog_class(name: str):
    return DIALOG_REGISTRY.get(name)
