import sys
import random
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QGraphicsView, QGraphicsScene, 
                             QComboBox, QLabel, QMessageBox, QGroupBox, QLineEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from components import ResistorItem, InductorItem, CapacitorItem
from math_engine import RLCCalculator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Amortiguamiento RLC")
        self.resize(1200, 750)
        
        self.current_mode = "Construir Circuito"
        
        # Variables para el modo Construir
        self.target_w0 = 0.0
        self.target_alpha = 0.0
        self.target_circuit_type = "Serie" # "Serie" o "Paralelo"
        
        # Variables para el modo Adivinar (Análisis)
        self.guess_question_type = 0
        self.guess_correct_answer_str = ""
        self.guess_correct_answer_num = 0.0
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Panel Izquierdo
        left_panel = QVBoxLayout()
        
        # --- Menú de Ejercicios ---
        exercise_group = QGroupBox("Configuración del Ejercicio")
        exercise_layout = QVBoxLayout()
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modo de Ejercicio:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Construir Circuito", "Modo Análisis"])
        self.combo_mode.currentTextChanged.connect(self.change_mode)
        mode_layout.addWidget(self.combo_mode)
        exercise_layout.addLayout(mode_layout)
        
        self.dynamic_panel = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_panel)
        self.dynamic_layout.setContentsMargins(0,0,0,0)
        
        # Widgets para "Construir Circuito"
        self.build_widget = QWidget()
        build_layout = QVBoxLayout(self.build_widget)
        build_layout.setContentsMargins(0,0,0,0)
        
        self.lbl_build_target = QLabel("Objetivo: ...")
        self.lbl_build_target.setFont(QFont("Arial", 11))
        self.lbl_build_target.setStyleSheet("color: blue;")
        build_layout.addWidget(self.lbl_build_target)
        
        self.btn_new_build = QPushButton("Generar Nuevo Reto")
        self.btn_new_build.clicked.connect(self.generate_new_build_target)
        build_layout.addWidget(self.btn_new_build)
        
        # Widgets para "Modo Análisis"
        self.guess_widget = QWidget()
        guess_layout = QVBoxLayout(self.guess_widget)
        guess_layout.setContentsMargins(0,0,0,0)
        
        self.lbl_guess_question = QLabel("Pregunta: ...")
        self.lbl_guess_question.setFont(QFont("Arial", 12))
        self.lbl_guess_question.setStyleSheet("color: blue;")
        self.lbl_guess_question.setWordWrap(True)
        guess_layout.addWidget(self.lbl_guess_question)
        
        guess_controls = QHBoxLayout()
        guess_controls.addWidget(QLabel("Tu respuesta:"))
        
        self.combo_guess = QComboBox()
        self.combo_guess.addItems(["Subamortiguado", "Sobreamortiguado", "Críticamente Amortiguado"])
        guess_controls.addWidget(self.combo_guess)
        
        self.input_guess = QLineEdit()
        self.input_guess.setPlaceholderText("Ej. 100.5")
        guess_controls.addWidget(self.input_guess)
        
        self.btn_new_guess = QPushButton("Siguiente Pregunta")
        self.btn_new_guess.clicked.connect(self.generate_new_guess)
        guess_controls.addWidget(self.btn_new_guess)
        
        guess_layout.addLayout(guess_controls)
        
        self.dynamic_layout.addWidget(self.build_widget)
        self.dynamic_layout.addWidget(self.guess_widget)
        
        exercise_layout.addWidget(self.dynamic_panel)
        exercise_group.setLayout(exercise_layout)
        left_panel.addWidget(exercise_group)
        # ----------------------------------
        
        # Controles de construcción
        self.controls_layout = QHBoxLayout()
        
        self.btn_add_r = QPushButton("Añadir Resistencia")
        self.btn_add_r.clicked.connect(lambda: self.add_component('R'))
        
        self.btn_add_l = QPushButton("Añadir Inductor")
        self.btn_add_l.clicked.connect(lambda: self.add_component('L'))
        
        self.btn_add_c = QPushButton("Añadir Capacitor")
        self.btn_add_c.clicked.connect(lambda: self.add_component('C'))
        
        self.circuit_type = QComboBox()
        self.circuit_type.addItems(["Serie", "Paralelo"])
        self.circuit_type.currentTextChanged.connect(self.update_simulation)
        
        self.btn_evaluate = QPushButton("Evaluar Ejercicio")
        self.btn_evaluate.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.btn_evaluate.clicked.connect(self.evaluate_circuit)
        
        self.controls_layout.addWidget(self.btn_add_r)
        self.controls_layout.addWidget(self.btn_add_l)
        self.controls_layout.addWidget(self.btn_add_c)
        self.controls_layout.addWidget(QLabel("Topología:"))
        self.controls_layout.addWidget(self.circuit_type)
        
        left_panel.addLayout(self.controls_layout)
        left_panel.addWidget(self.btn_evaluate)
        
        # Escena Gráfica
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints().Antialiasing)
        left_panel.addWidget(self.view)
        
        main_layout.addLayout(left_panel, stretch=2)
        
        # Panel Derecho: Resultados y Gráfica
        right_panel = QVBoxLayout()
        
        self.lbl_results = QLabel("Resultados Calculados:\nω0 = -- rad/s\nα = -- Np/s\nTipo = --")
        self.lbl_results.setFont(QFont("Arial", 11))
        right_panel.addWidget(self.lbl_results)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Respuesta en el Tiempo")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Respuesta")
        self.ax.grid(True)
        right_panel.addWidget(self.canvas)
        
        self.lbl_grade = QLabel("Calificación: --")
        self.lbl_grade.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        right_panel.addWidget(self.lbl_grade)
        
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setFont(QFont("Arial", 10))
        self.lbl_feedback.setStyleSheet("color: orange;")
        self.lbl_feedback.setWordWrap(True)
        right_panel.addWidget(self.lbl_feedback)
        
        main_layout.addLayout(right_panel, stretch=1)
        
        self.components = []
        
        # Inicializar UI según el modo
        self.change_mode("Construir Circuito")

    def change_mode(self, mode):
        self.current_mode = mode
        self.lbl_grade.setText("Calificación: --")
        self.lbl_grade.setStyleSheet("color: black;")
        self.lbl_feedback.setText("")
        
        if mode == "Construir Circuito":
            self.build_widget.show()
            self.guess_widget.hide()
            self.view.show()
            self.btn_add_r.setEnabled(True)
            self.btn_add_l.setEnabled(True)
            self.btn_add_c.setEnabled(True)
            self.circuit_type.setEnabled(True)
            self.lbl_results.show()
            self.ax.clear()
            self.canvas.draw()
            self.generate_new_build_target()
        else:
            self.build_widget.hide()
            self.guess_widget.show()
            self.view.hide()
            self.btn_add_r.setEnabled(False)
            self.btn_add_l.setEnabled(False)
            self.btn_add_c.setEnabled(False)
            self.circuit_type.setEnabled(False)
            self.lbl_results.hide()
            self.ax.clear()
            self.canvas.draw()
            self.generate_new_guess()

    def generate_new_build_target(self):
        # Generar w0 y alpha objetivos
        self.target_w0 = round(random.uniform(50.0, 500.0), 1)
        # 33% chance of each damping type roughly
        choice = random.choice([0, 1, 2])
        if choice == 0: # Subamortiguado
            self.target_alpha = round(random.uniform(5.0, self.target_w0 - 5.0), 1)
        elif choice == 1: # Sobreamortiguado
            self.target_alpha = round(random.uniform(self.target_w0 + 10.0, self.target_w0 * 3), 1)
        else: # Crítico
            self.target_alpha = self.target_w0
            
        self.target_circuit_type = random.choice(["Serie", "Paralelo"])
        
        self.lbl_build_target.setText(
            f"<b>Objetivo a Construir:</b> Circuito RLC <b>{self.target_circuit_type}</b><br>"
            f"Frecuencia de Resonancia (ω0): {self.target_w0} rad/s<br>"
            f"Frec. de Amortiguamiento (α): {self.target_alpha} Np/s"
        )
        self.lbl_grade.setText("Calificación: --")
        self.lbl_grade.setStyleSheet("color: black;")
        self.lbl_feedback.setText("")

    def generate_new_guess(self):
        self.guess_question_type = random.randint(1, 4)
        self.lbl_grade.setText("Calificación: --")
        self.lbl_grade.setStyleSheet("color: black;")
        self.lbl_feedback.setText("")
        
        # Generar un circuito base válido
        R = round(random.uniform(10, 100), 1)
        L = round(random.uniform(0.1, 2.0), 2)
        C = round(random.uniform(0.001, 0.05), 4)
        tipo_c = random.choice(["Serie", "Paralelo"])
        
        if tipo_c == "Serie":
            w0, alpha, tipo = RLCCalculator.calculate_series(R, L, C)
        else:
            w0, alpha, tipo = RLCCalculator.calculate_parallel(R, L, C)
            
        w0 = round(w0, 2)
        alpha = round(alpha, 2)

        if self.guess_question_type == 1:
            # Adivinar tipo dados w0 y alpha
            self.combo_guess.show()
            self.input_guess.hide()
            self.guess_correct_answer_str = tipo
            self.lbl_guess_question.setText(
                f"Dado un circuito con ω0 = {w0} rad/s y α = {alpha} Np/s.\n"
                "¿Qué tipo de respuesta tiene el sistema?"
            )
            
        elif self.guess_question_type == 2:
            # Calcular w0 dados R, L, C
            self.combo_guess.hide()
            self.input_guess.show()
            self.input_guess.clear()
            self.guess_correct_answer_num = w0
            self.lbl_guess_question.setText(
                f"Circuito {tipo_c} con R = {R} Ω, L = {L} H, C = {C} F.\n"
                "Calcula la Frecuencia de Resonancia (ω0) en rad/s:"
            )
            
        elif self.guess_question_type == 3:
            # Calcular alpha dados R, L, C
            self.combo_guess.hide()
            self.input_guess.show()
            self.input_guess.clear()
            self.guess_correct_answer_num = alpha
            self.lbl_guess_question.setText(
                f"Circuito {tipo_c} con R = {R} Ω, L = {L} H, C = {C} F.\n"
                "Calcula la Frecuencia de Amortiguamiento (α) en Np/s:"
            )
            
        elif self.guess_question_type == 4:
            # Encontrar componente faltante (ej. R dado w0, L, C... para variar usamos alpha y R,L,C)
            self.combo_guess.hide()
            self.input_guess.show()
            self.input_guess.clear()
            
            # Decidimos ocultar C y dar w0 y L. w0 = 1/sqrt(LC) => C = 1/(L * w0^2)
            self.guess_correct_answer_num = C
            self.lbl_guess_question.setText(
                f"Para lograr un ω0 = {w0} rad/s en un circuito con L = {L} H.\n"
                "¿Cuál debe ser el valor del Capacitor (C) en Faradios?"
            )

    def add_component(self, comp_type):
        if comp_type == 'R':
            item = ResistorItem()
        elif comp_type == 'L':
            item = InductorItem()
        elif comp_type == 'C':
            item = CapacitorItem()
            
        item.setPos(random.randint(50, 250), random.randint(50, 250))
        self.scene.addItem(item)
        self.components.append(item)

    def update_simulation(self):
        if self.current_mode != "Construir Circuito":
            return None, None
            
        R = sum([c.value for c in self.components if c.name == 'R'])
        L = sum([c.value for c in self.components if c.name == 'L'])
        C = sum([c.value for c in self.components if c.name == 'C'])
        
        tipo_c = self.circuit_type.currentText()
        
        if R == 0 or L == 0 or C == 0:
            self.lbl_results.setText("Faltan componentes o valores para simular el RLC.")
            self.ax.clear()
            self.canvas.draw()
            return None, None
            
        if tipo_c == "Serie":
            w0, alpha, tipo = RLCCalculator.calculate_series(R, L, C)
        else:
            w0, alpha, tipo = RLCCalculator.calculate_parallel(R, L, C)
            
        self.lbl_results.setText(f"Resultados:\nω0 = {w0:.2f} rad/s\nα = {alpha:.2f} Np/s\nTipo = {tipo}")
        
        t, y = RLCCalculator.get_time_response(R, L, C, tipo_c)
        self.ax.clear()
        self.ax.plot(t, y, label=f"Respuesta {tipo}")
        self.ax.set_title("Respuesta en el Tiempo")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Respuesta")
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()
        
        return w0, alpha

    def evaluate_circuit(self):
        self.lbl_feedback.setText("")
        if self.current_mode == "Construir Circuito":
            w0, alpha = self.update_simulation()
            
            if w0 is None:
                QMessageBox.warning(self, "Error", "El circuito está incompleto. Asegúrate de tener R, L y C con valores mayores a 0.")
                self.lbl_grade.setText("Calificación: 0/100")
                self.lbl_grade.setStyleSheet("color: red;")
                self.show_explosion()
                return
                
            if self.circuit_type.currentText() != self.target_circuit_type:
                self.lbl_grade.setText("Calificación: 0/100")
                self.lbl_grade.setStyleSheet("color: red;")
                self.lbl_feedback.setText("¡Construiste la topología equivocada! Revisa si pedía Serie o Paralelo.")
                self.show_explosion()
                return

            error_w0 = abs(w0 - self.target_w0) / self.target_w0 if self.target_w0 != 0 else 0
            error_alpha = abs(alpha - self.target_alpha) / self.target_alpha if self.target_alpha != 0 else 0
            
            max_error = max(error_w0, error_alpha)
            
            if max_error <= 0.05: # 5% de error permitido para 100
                self.lbl_grade.setText("Calificación: 100/100 - ¡Excelente!")
                self.lbl_grade.setStyleSheet("color: green;")
                self.show_success_animation()
            elif max_error <= 0.20: # 20% de error permitido para 50
                self.lbl_grade.setText("Calificación: 50/100 - Regular")
                self.lbl_grade.setStyleSheet("color: orange;")
                
                # Feedback
                if error_w0 > error_alpha:
                    msg = "Tu ω0 está desfasado. Ajusta el Capacitor o el Inductor."
                else:
                    msg = "Tu α está desfasado. Revisa la Resistencia."
                self.lbl_feedback.setText(msg)
            else:
                self.lbl_grade.setText("Calificación: 0/100 - ¡Error!")
                self.lbl_grade.setStyleSheet("color: red;")
                self.lbl_feedback.setText("Los valores están muy lejos del objetivo (>20% error).")
                self.show_explosion()
                
        elif self.current_mode == "Modo Análisis":
            if self.guess_question_type == 1:
                user_guess = self.combo_guess.currentText()
                is_correct = (user_guess == self.guess_correct_answer_str)
            else:
                try:
                    user_val = float(self.input_guess.text())
                    # Permitir 2% de error debido al redondeo que pedimos
                    error = abs(user_val - self.guess_correct_answer_num) / (self.guess_correct_answer_num if self.guess_correct_answer_num != 0 else 1)
                    is_correct = (error <= 0.02)
                except ValueError:
                    is_correct = False
            
            if is_correct:
                self.lbl_grade.setText("Calificación: 100/100 - ¡Correcto!")
                self.lbl_grade.setStyleSheet("color: green;")
                self.show_success_animation()
            else:
                self.lbl_grade.setText("Calificación: 0/100 - ¡Incorrecto!")
                self.lbl_grade.setStyleSheet("color: red;")
                self.lbl_feedback.setText(f"La respuesta correcta era cercana a: {self.guess_correct_answer_num if self.guess_question_type != 1 else self.guess_correct_answer_str}")
                self.show_explosion()

    def show_explosion(self):
        if self.current_mode == "Construir Circuito":
            self.scene.clear()
            self.components = []
            boom_text = self.scene.addText("¡BOOM!\nCortocircuito")
            boom_text.setFont(QFont("Comic Sans MS", 40, QFont.Weight.Bold))
            boom_text.setDefaultTextColor(Qt.GlobalColor.red)
            boom_text.setPos(50, 50)
            
        self._shake_count = 0
        self._original_pos = self.pos()
        self.shake_timer = QTimer(self)
        self.shake_timer.timeout.connect(self.do_shake)
        self.shake_timer.start(50)

    def do_shake(self):
        self._shake_count += 1
        if self._shake_count > 10:
            self.shake_timer.stop()
            self.move(self._original_pos)
        else:
            dx = random.randint(-20, 20)
            dy = random.randint(-20, 20)
            self.move(self._original_pos.x() + dx, self._original_pos.y() + dy)

    def show_success_animation(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("¡Felicidades!")
        msg.setText("¡Respuesta correcta!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
