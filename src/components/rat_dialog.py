from src.components.generic_form_dialog import GenericFormDialog
from PySide6.QtWidgets import QComboBox, QMessageBox, QApplication, QDateEdit, QLineEdit, QTextEdit, QCheckBox, QLabel
from PySide6.QtCore import Qt, QTimer, QDate
from pathlib import Path
import json

# Ajusta el import según tu estructura real
from src.core.api_client import ApiClient

class RatDialog(GenericFormDialog):
    RAT_CATALOGO_CACHE_KEY = "catalogo_rat_id"

    def __init__(self, parent=None, rat_id=None, **kwargs):
        # 1. CONFIGURACIÓN DE RUTAS
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.config_ia_path = base_dir / "src" / "config" / "formularios" / "rat_ia.json"
        self.config_institucional_path = base_dir / "src" / "config" / "formularios" / "rat_institucional.json"
        self.config_simplificado_path = base_dir / "src" / "config" / "formularios" / "rat_simplificado.json"
        
        config_path = base_dir / "src" / "config" / "formularios" / "rat.json"
        
        target_id = rat_id
        if target_id is None: target_id = kwargs.get("id")
        if target_id is None: target_id = kwargs.get("record_id")
        
        self._current_extension = None
        self.client = ApiClient()
        self._is_admin_user = self.client.is_admin
        self._is_auditor_user = self.client.is_auditor
        
        self.rat_estado = "EN_EDICION"

        super().__init__(str(config_path), parent=parent, record_id=target_id)
        
        # 2. CONEXIÓN DE SEÑALES (SOLO CREAR)
        if "tipo_tratamiento" in self.inputs:
            combo = self.inputs["tipo_tratamiento"]
            if isinstance(combo, QComboBox):
                combo.currentIndexChanged.connect(self._check_type_transition)

    # =========================================================================
    #  LÓGICA DE EXPANSIÓN DINÁMICA (UI)
    # =========================================================================
  
    def _check_type_transition(self): 
        """Se ejecuta al cambiar el combo manualmente (Usuario)."""
        combo = self.inputs.get("tipo_tratamiento")
        if not combo: return
        val = combo.currentData()
        # Aseguramos string para la comparación
        val_str = str(val) if val else None
        self._perform_expansion(val_str)

    def _perform_expansion(self, tipo_uuid):
        """Carga/Descarga secciones según el UUID."""
        target_config = None
        target_name = None
        
        # IDs según tu Base de Datos
        if tipo_uuid == "df15ad81-74f8-4f1d-8e4a-d92b5b7ece44":  # IA
            target_config = self.config_ia_path
            target_name = "ia"
        elif tipo_uuid == "53d1a722-5311-41d1-a2b6-9bbae7ea037b":  # Institucional
            target_config = self.config_institucional_path
            target_name = "institucional"
        elif tipo_uuid in ["85dd61f7-ab43-462c-ae45-f046812d0695", "1f3e71b0-99d4-41e1-a855-ec65377a6321", 
                           "e295e4a8-6622-4c9a-ad47-78da7b36572c", "e42ae6e9-95d9-43e5-894a-ce6bb663bfa0", 
                           "8a06e8c5-8055-40ee-8855-5d7f3f693ca0"]:  # Simplificado
            target_config = self.config_simplificado_path
            target_name = "simplificado"
            
        if target_name != self._current_extension:
            if self._current_extension: self._shrink_form()
            if target_config:
                self._expand_form(target_config)
                self._current_extension = target_name
            else:
                self._current_extension = None

    def _expand_form(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                ext_config = json.load(f)
        except Exception:
            return

        sections = ext_config.get("sections", [])
        if not sections:
            return

        # 🚨 SIEMPRE saltar las 2 primeras
        new_sections = sections[2:]

        if not new_sections:
            return

        start_index = len(self.config["sections"])
        self.config["sections"].extend(new_sections)

        for i, section in enumerate(new_sections):
            abs_index = start_index + i
            content_widget = self._build_section_form(section)
            self.sidebar.add_step(section["title"])

            page = self._wrap_step_content(
                content_widget,
                section["title"],
                section.get("description", ""),
                abs_index,
                len(self.config["sections"]),
            )
            self.stack.addWidget(page)
            self._load_new_combos(section)

        if start_index > 0:
            self._update_footer_to_next(start_index - 1)
        
        last_index = self.stack.count() - 1
        self._update_footer_to_save(last_index)

        self._validate_steps_progress()

    def _shrink_form(self):
        if len(self.config["sections"]) <= 2: return
        while len(self.config["sections"]) > 2:
            section = self.config["sections"].pop()
            for field in section.get("fields", []):
                key = field["key"]
                if key in self.inputs: del self.inputs[key]
                if key in self.dependencies: del self.dependencies[key]
                if key in self.dependency_configs: del self.dependency_configs[key]
            
            self.sidebar.remove_last_step()
            w = self.stack.widget(self.stack.count()-1)
            self.stack.removeWidget(w); w.deleteLater()
            
        self._update_footer_to_save(1)
        self._validate_steps_progress()

    def _load_new_combos(self, section):
        for field in section.get("fields", []):
            if field.get("type") == "combo" and field.get("source") and not field.get("depends_on"):
                key = field["key"]
                if key in self.inputs:
                    self._start_combo_loader(self.inputs[key], field["source"], field.get("cache_key"))

    # --- Helpers Footer ---
    def _update_footer_to_next(self, idx): self._rebuild_footer(idx, False)
    def _update_footer_to_save(self, idx): self._rebuild_footer(idx, True)
    
    def _rebuild_footer(self, index, is_last):
        page = self.stack.widget(index)
        if not page:
            return

        layout = page.layout()
        if not layout:
            return

        item = layout.itemAt(layout.count() - 1)
        if item:
            self._clear_layout(item.layout())

        from PySide6.QtWidgets import QPushButton

        # Botón Anterior
        if index > 0:
            btn_prev = QPushButton("Anterior")
            btn_prev.setObjectName("secondaryButton")
            btn_prev.clicked.connect(self.sidebar.prev_step)
            item.layout().addWidget(btn_prev)

        item.layout().addStretch()

        if not is_last:
            btn_next = QPushButton("Siguiente")
            btn_next.setObjectName("primaryButton")
            btn_next.clicked.connect(self.sidebar.next_step)
            item.layout().addWidget(btn_next)
            return

        # ===============================
        # DECISIÓN DE BOTONES (AQUÍ ESTÁ TODO)
        # ===============================

        estado = self.rat_estado
        is_admin = self._is_admin_user

        if estado == "EN_EDICION":
            btn_guardar = QPushButton("Guardar")
            btn_guardar.setObjectName("primaryButton")
            btn_guardar.clicked.connect(self._submit)

            btn_enviar = QPushButton("Enviar")
            btn_enviar.setObjectName("dangerButton")
            btn_enviar.clicked.connect(self._submit_enviar)

            item.layout().addWidget(btn_guardar)
            item.layout().addWidget(btn_enviar)

        elif estado == "ENVIADO" and is_admin:
            btn_aprobar = QPushButton("Aprobar")
            btn_aprobar.setObjectName("successButton")
            btn_aprobar.clicked.connect(self._aprobar_rat)

            btn_rechazar = QPushButton("Rechazar")
            btn_rechazar.setObjectName("dangerButton")
            btn_rechazar.clicked.connect(self._mostrar_rechazo)

            item.layout().addWidget(btn_aprobar)
            item.layout().addWidget(btn_rechazar)

    # APROBADO / ENVIADO (no admin) / otros
    # → no se muestran botones

        
    
    def _submit_enviar(self):
        try:
            if not self.record_id:
                QMessageBox.warning(
                    self,
                    "No enviado",
                    "Debe guardar el RAT antes de enviarlo."
                )
                return

            QApplication.setOverrideCursor(Qt.WaitCursor)

            # 🔒 SOLO cambiar estado
            self.client.put(
            f"/rat/{self.record_id}/estado",
            {"estado": "ENVIADO"}
)

            self._invalidate_rat_catalog_cache()

            QApplication.restoreOverrideCursor()

            QMessageBox.information(
                self,
                "RAT enviado",
                "El RAT fue enviado correctamente y ya no puede ser editado."
            )

            self.accept()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", str(e))
    
    def _aprobar_rat(self):
        self.client.put(
            f"/rat/{self.record_id}/estado",
            {"estado": "APROBADO"}
        )
        self._invalidate_rat_catalog_cache()
        QMessageBox.information(self, "RAT aprobado", "El RAT fue aprobado.")
        self.accept()
        
    def _mostrar_rechazo(self):
        from PySide6.QtWidgets import QInputDialog

        comentario, ok = QInputDialog.getMultiLineText(
            self,
            "Rechazar RAT",
            "Ingrese el motivo del rechazo:"
        )

        if ok and comentario.strip():
            self.client.put(
                f"/rat/{self.record_id}/estado",
                {
                    "estado": "RECHAZADO",
                    "comentario": comentario
                }
            )
            self._invalidate_rat_catalog_cache()
            QMessageBox.information(self, "RAT rechazado", "El RAT fue rechazado.")
            self.accept()


    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

   # =========================================================================
    #  CARGA DE DATOS (EDITAR) - SOLUCIÓN ROBUSTA SIN TRADUCCIONES
    # =========================================================================
    def _lock_form(self):
        for w in self.inputs.values():
            w.setEnabled(False)

    def _on_record_data(self, data):
        
        self.rat_estado = data.get("estado", "EN_EDICION")

        if self.rat_estado in ["ENVIADO", "APROBADO", "RECHAZADO"]:
            self._lock_form()

        if not data:
            return

        # 🔁 MAPEO BACKEND → FORM
        key_map = {
            "subsecretaria_id": "subsecretaria",
            "division_id": "division",
            "responsable_tratamiento": "nombre_responsable",
            "encargado_tratamiento": "nombre_encargado",
        }

        for backend_key, form_key in key_map.items():
            if backend_key in data and form_key not in data:
                data[form_key] = data.get(backend_key)

        # Expandir secciones según tipo
        tid = data.get("tipo_tratamiento")
        if tid:
            self._perform_expansion(str(tid))
        
        last_index = self.stack.count() - 1
        self._rebuild_footer(last_index, True)
        print("ESTADO RAT:", self.rat_estado, "ADMIN:", self._is_admin_user)


        self.asset_data = data


        

    
    # =========================================================================
    #  GUARDADO (SUBMIT) - SOLUCIÓN AL ERROR 422
    # =========================================================================

    def _submit(self):
        # 1. Obtenemos datos LIMPIOS (None si están vacíos)
        form_data = self._get_all_form_values()

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            if self.record_id:
                # MODO EDICIÓN
                self.client.put(f"/rat/{self.record_id}", form_data)
                self._save_sections_by_type(form_data)
            else:
                # MODO CREACIÓN
                
                # Validamos campos OBLIGATORIOS para evitar 422
                if not form_data.get("subsecretaria") or not form_data.get("tipo_tratamiento"):
                    raise Exception("Debe seleccionar Subsecretaría y Tipo de Tratamiento.")
                
                if self._current_extension == "ia":
                    tipo_rat = "IA"
                elif self._current_extension == "institucional":
                    tipo_rat = "PROCESO"
                elif self._current_extension == "simplificado":
                    tipo_rat = "SIMPLIFICADO"
                else:
                    tipo_rat = "IA"  # fallback seguro


                payload_create = {
                    "nombre_tratamiento": form_data.get("nombre_tratamiento"),
                    "tipo_tratamiento": form_data.get("tipo_tratamiento"),
                    "subsecretaria_id": form_data.get("subsecretaria"),
                    "division_id": form_data.get("division"),
                    "departamento": form_data.get("departamento"),
                    "responsable_tratamiento": form_data.get("nombre_responsable"),
                    "cargo_responsable": form_data.get("cargo_responsable"),
                    "email_responsable": form_data.get("email_responsable"),
                    "telefono_responsable": form_data.get("telefono_responsable"),

                    "encargado_tratamiento": form_data.get("nombre_encargado"),
                    "cargo_encargado": form_data.get("cargo_encargado"),
                    "email_encargado": form_data.get("email_encargado"),
                    "telefono_encargado": form_data.get("telefono_encargado"),
                    "estado": "EN_EDICION",
                    "tipo_rat": tipo_rat,  # Tu backend probablemente exige esto
                    "tipo_tratamiento_otro": "N/A"
                    
                }
                
                
  
                
                # Imprimimos payload para debug si vuelve a fallar
                print(f"Enviando POST /rat: {payload_create}")

                res = self.client.post("/rat", payload_create)
                self.record_id = res.get("rat_id")
                
                if self.record_id:
                    self._save_gobierno_datos(form_data)
                    
                    if self._current_extension == "ia": 
                        self._save_seccion_ia(form_data)
                    elif self._current_extension == "institucional":
                        self._save_seccion_institucional(form_data)
                    elif self._current_extension == "simplificado":
                        self._save_seccion_simplificado(form_data)
                        
                    self._save_riesgos(form_data)
                    self._save_conclusion(form_data)

            self._invalidate_rat_catalog_cache()
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Éxito", "Guardado correctamente.")
            self.accept()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            print(f"Error submit: {e}")
            # Mostrar mensaje amigable si es error de validación
            msg = str(e)
            if "422" in msg: msg = "Faltan campos obligatorios o el formato es incorrecto."
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{msg}")

    def _invalidate_rat_catalog_cache(self):
        self.catalogo_service.invalidate_cache_key(self.RAT_CATALOGO_CACHE_KEY)

    # --- Helpers Guardado ---
    def _save_gobierno_datos(self, data):
        payload = {
            "fecha_elaboracion": data.get("fecha_elaboracion"),
            "responsable_informe": data.get("responsable_informe"),
            "equipo_entrevistados": data.get("equipo_entrevistados"),
            "equipo_validacion_contenidos": data.get("equipo_validacion"),
            "revision_aprobacion_final": data.get("revision_aprobacion")
        }
        self.client.put(f"/rat/{self.record_id}/gobierno-datos", payload)

    def _save_seccion_ia(self, data):
        base = f"/rat/{self.record_id}/ia"
        self.client.put(f"{base}/finalidad", {
            "finalidad_principal_uso_ia": data.get("finalidad_principal_ia"),
            "tipo_tarea_ia": data.get("tipo_tarea_ia"),
            "alcance_impacto": data.get("alcance_impacto_ia"),
            "efectos_juridicos_significativos": data.get("efectos_juridicos_ia")
        })
        self.client.put(f"{base}/flujo", {
            "descripcion_flujo_ia": data.get("descripcion_resumida_flujo_ia"),
            "puntos_intervencion_humana": data.get("puntos_intervencion_ia"),
            "sistemas_repositorios_involucrados": data.get("sistemas_repositorios_ia")
        })
        self.client.put(f"{base}/entrenamiento", {
            "fuentes_datos_entrenamiento": data.get("fuente_datos_entrenamiento_ia"),
            "base_licitud": data.get("base_licitud_entrenamiento_ia"),
            "restricciones_uso": data.get("restricciones_uso_ia"),
            "categorias_datos_personales": data.get("categorias_datos_entrenamiento_ia"),
            "datos_sensibles": bool(data.get("datos_sensibles_entrenamiento_ia")),
            "volumen_y_periodo": data.get("volumen_periodo_ia"),
            "poblaciones_especiales": data.get("poblaciones_vulnerables_entrenamiento_ia")
        })
        self.client.put(f"{base}/operacional", {
             "datos_entrada": data.get("datos_entrada_ia"),
             "datos_salida": data.get("datos_salida_ia"),
             "monitoreo_modelo": data.get("monitoreo_modelo_ia")
        })
        self.client.put(f"{base}/modelo", {
            "tipo_modelo": data.get("tipo_modelo_ia"),
            "modalidad_entrenamiento": data.get("modalidad_entrenamiento_ia"),
            "infraestructura_ejecucion": data.get("infraestructura_ejecucion_ia"),
            "reentrenamiento": data.get("reentrenamiento_ia"),
            "controles_acceso": data.get("controles_acceso_ia")
        })
        self.client.put(f"{base}/explicabilidad", {
            "campo": "general",
            "explicacion_logica_aplicada": data.get("explicacion_logica_ia"),
            "variables_relevantes": data.get("variables_relevantes_ia"),
            "intervencion_humana": data.get("intervencion_humana_ia"),
            "documentacion_explicabilidad_path": data.get("documentacion_explicabilidad_ia")
        })

    def _save_seccion_simplificado(self, data):
        # 1. Guardamos la parte principal (Simplificado)
        payload_simp = {
        # =========================
        # DESCRIPCIÓN DEL TRATAMIENTO
        # =========================
        "autorizacion_datos": data.get("autorizacion_datos_ris"),

        # ⚠️ NOMBRES QUE EXIGE EL BACKEND
        "descripcion": data.get("descripcion_alcance"),
        "operaciones": data.get("operaciones_realizadas"),
        "equipos_ejecutantes": data.get("equipos_involucrados"),

        "software": data.get("software_utilizado"),
        "repositorios": data.get("repositorios_utilizados"),
        "sistemas": data.get("sistemas_plataformas"),

        # =========================
        # MARCO HABILITANTE
        # =========================
        "mecanismo_habilitante": data.get("mecanismo_habilitante"),
        "mecanismo_habilitante_otro": data.get("mecanismo_habilitante_otro"),
        "nombre_mecanismo": data.get("nombre_mecanismo"),

        "consentimiento_titular": data.get("consentimiento_titular"),
        "finalidad_tratamiento": data.get("finalidad_tratamiento"),

        # =========================
        # ⚠️ ESTO FALTABA Y ROMPÍA TODO
        # =========================
        "categoria_destinatarios": data.get("categorias_destinatarios"),
        "categoria_destinatarios_otro": data.get("categoria_destinatarios_otro"),

        # =========================
        # VOLUMEN
        # =========================
        "volumen_datos": data.get("volumen_datos"),
        "cantidad_archivos": data.get("cantidad_archivos"),

        # =========================
        # BOOLEANOS
        # =========================
        "decisiones_automatizadas": (
            str(data.get("decisiones_automatizadas")).lower() in ["si", "true", "1"]
        ),
    
    }
        
        self.client.put(f"/rat/{self.record_id}/simplificado", payload_simp)
        
        # 2. Guardamos la sección de Titulares
        try:
            # Categorías de datos personales (MULTI)
            cat_datos = data.get("categorias_datos_personales", [])
            if isinstance(cat_datos, list):
                cat_datos = json.dumps(cat_datos)

            # Categorías de destinatarios (SINGLE)
            cat_destinatarios = data.get("categorias_destinatarios")

            # Poblaciones vulnerables (MULTI)
            pob_vulnerable = data.get("poblaciones_vulnerables", [])
            if isinstance(pob_vulnerable, list):
                pob_vulnerable = json.dumps(pob_vulnerable)

            payload_titulares = {
                # 🔹 DATOS PERSONALES
                "categoria_datos": cat_datos,

                # 🔹 DESTINATARIOS
                "categoria_datos_especificacion": data.get("categorias_destinatarios"),

                # 🔹 POBLACIONES
                "poblaciones_especiales": pob_vulnerable,
                "poblaciones_especiales_otro": data.get("poblaciones_vulnerables_otro"),

                # 🔹 OTROS
                "tipo_datos": data.get("tipos_datos"),
                "origen_datos": data.get("origen_datos"),
                "origen_datos_otro": data.get("origen_datos_otro"),
                "medio_recoleccion": data.get("medio_recoleccion"),

                "volumen_datos": data.get("volumen_datos"),
                "cantidad_archivos": data.get("cantidad_archivos"),

                "decisiones_automatizadas": (
                    str(data.get("decisiones_automatizadas")).lower() in ["si", "true", "1"]
                ),
            }
            self.client.put(f"/rat/{self.record_id}/titulares", payload_titulares)
            
        except Exception as e:
            print(f"Error guardando titulares: {e}")
            
    def _save_seccion_institucional(self, data):
        # Mapeo de llaves del Formulario (Frontend) -> Esquema del Backend
        payload = {
            "descripcion": data.get("descripcion_alcance"),
            "operaciones": data.get("operaciones_realizadas"),
            "equipos_ejecutantes": data.get("equipos_involucrados"),
            "software": data.get("aplicaciones_software"),
            "repositorios": data.get("repositorios_utilizados"),
            "sistemas": data.get("sistemas_plataformas_desc"),
            
            "finalidad_tratamiento": data.get("finalidad_tratamiento_inst"),
            "resultado_esperado": data.get("resultados_esperados"),
            
            "mecanismo_habilitante": data.get("base_licitud_inst"),
            # --- AQUÍ ESTABA EL ERROR: Faltaba esta llave ---
            "mecanismo_habilitante_otro": data.get("mecanismo_habilitante_otro"), 
            "nombre_mecanismo": data.get("nombre_mecanismo"),
            
            # Origen y Ciclo de vida
            "fuente_datos": data.get("fuente_datos"),
            "medio_recoleccion": data.get("medio_recoleccion_origen"),
            "forma_recoleccion": data.get("forma_recoleccion"),
            "uso_tratamiento": data.get("uso_tratamiento"),
            "almacenamiento_conservacion": data.get("almacenamiento_conservacion"),
            "comunicacion_transferencia": data.get("comunicacion_transferencia"),
            "destinatario_fundamento_legal": data.get("destinatarios_fundamento"),
            "disposicion_final": data.get("eliminacion_disposicion"),
            
            # Flujos y Conclusión
            "flujos_descripcion": data.get("descripcion_flujos"), 
            "flujos_sistemas": data.get("sistemas_plataformas_flujos"),
            
            "documentos_respaldo": data.get("documentos_respaldo"),
        }
        # Llamada al endpoint específico de Institucional
        self.client.put(f"/rat/{self.record_id}/proceso", payload)
        
         # Categorías de datos personales (MULTI)
        cat_datos = data.get("categorias_datos_inst", [])
        if isinstance(cat_datos, list):
            cat_datos = json.dumps(cat_datos)

            # Poblaciones vulnerables (MULTI)
        pob_vulnerable = data.get("poblaciones_vulnerables_inst", [])
        if isinstance(pob_vulnerable, list):
            pob_vulnerable = json.dumps(pob_vulnerable)
        
        payload_titulares = {
                # 🔹 DATOS PERSONALES
                "categoria_datos": cat_datos,
                # 🔹 POBLACIONES
                "poblaciones_especiales": pob_vulnerable,

                # 🔹 OTROS
                "tipo_datos": data.get("tipos_datos"),
                "origen_datos": data.get("origen_datos_titulares"),
                "medio_recoleccion": data.get("medio_recoleccion_titulares"),

                "volumen_datos": data.get("volumen_datos"),
                "cantidad_archivos": data.get("cantidad_archivos"),

                "decisiones_automatizadas": (
                    str(data.get("decisiones_automatizadas")).lower() in ["si", "true", "1"]
                ),
            }
        self.client.put(f"/rat/{self.record_id}/titulares", payload_titulares)
            

    def _save_riesgos(self, data):
        if not data.get("nombre_riesgo") and not data.get("descripcion_riesgo"):
            return

        payload = {
            "nombre_riesgo": data.get("nombre_riesgo"),
            "descripcion_riesgo": data.get("descripcion_riesgo"),
        }

        self.client.post(f"/rat/{self.record_id}/riesgos", payload)
        
    def _save_conclusion(self, data):
        if not data.get("sintesis_analisis") and not data.get("justificacion"):
            return

        payload = {
            "sintesis_analisis": data.get("sintesis_analisis"),
            "corresponde_eipd": data.get("corresponde_eipd") == "si_corresponde",
            "justificacion": data.get("justificacion"),
        }

        self.client.put(f"/rat/{self.record_id}/conclusion", payload)

    def _get_all_form_values(self):
        """Recolector de datos BLINDADO contra 422."""
        vals = {}
        for k, w in self.inputs.items():
            if isinstance(w, QComboBox):
                # IMPORTANTE: Si es None, devolvemos None. NO el texto "Seleccione..."
                v = w.currentData()
                vals[k] = v 
            elif isinstance(w, QDateEdit): 
                vals[k] = w.date().toString("yyyy-MM-dd")
            elif hasattr(w, "text"): 
                t = w.text().strip()
                vals[k] = t if t else None
            elif hasattr(w, "toPlainText"): 
                t = w.toPlainText().strip()
                vals[k] = t if t else None
            elif hasattr(w, "selectedFiles"):
                f = w.selectedFiles()
                vals[k] = f[0] if f else None
        return vals
    
    def _save_sections_by_type(self, form_data):
        # Sección común
        self._save_gobierno_datos(form_data)

        # Sección específica según tipo
        if self._current_extension == "ia":
            self._save_seccion_ia(form_data)
        elif self._current_extension == "institucional":
            self._save_seccion_institucional(form_data)
        elif self._current_extension == "simplificado":
            self._save_seccion_simplificado(form_data)

        # Secciones finales comunes
        self._save_riesgos(form_data)
        self._save_conclusion(form_data)
