import os
from src.components.generic_grid_view import GenericGridView

class ActivosView(GenericGridView):
    def __init__(self):
        # Construct absolute path to config file
        # __file__ is .../src/views/activos/activos_view.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to 'src'
        # current_dir = .../src/views/activos
        # parent = .../src/views
        # grand = .../src
        src_dir = os.path.dirname(os.path.dirname(current_dir))
        
        config_path = os.path.join(src_dir, "config", "grillas", "activos.json")
        
        super().__init__(config_path=config_path)
