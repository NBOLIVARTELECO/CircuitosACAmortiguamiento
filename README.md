# Simulador Educativo de Circuitos RLC (Amortiguamiento AC)

¡Bienvenido al **Simulador Interactivo de Circuitos RLC**! Esta aplicación en Python (PyQt6) ha sido diseñada específicamente para estudiantes de ingeniería y electrónica que desean comprender el comportamiento de los circuitos RLC en serie y en paralelo, con un enfoque didáctico y gamificado.

## 🎯 Enfoque Pedagógico

El aprendizaje de ecuaciones diferenciales y circuitos de corriente alterna suele ser muy abstracto para los estudiantes. Esta herramienta ataca ese problema mediante:

1. **Interactividad Práctica:** En lugar de solo resolver fórmulas en papel, el estudiante puede usar una interfaz de "arrastrar y soltar" (Drag & Drop) para construir circuitos visualmente e introducir valores realistas.
2. **Evaluación Formativa y Calificación Parcial:** El sistema no castiga ciegamente. Si un estudiante falla por poco (error entre 5% y 20%), recibe un **50/100** y retroalimentación directa sobre qué variable física (Condensador, Inductor o Resistencia) debe ajustar para acercarse al objetivo.
3. **Consecuencias Visuales:** Para mantener el interés (Gamificación), un error grave (más del 20%) provoca una respuesta cómica e interactiva: ¡El circuito hace un cortocircuito ("BOOM!") y la ventana tiembla! Esto fomenta que el estudiante intente nuevamente hasta dominar el concepto.

---

## 🛠️ Modos de Juego / Ejercicio

La aplicación cuenta con dos modalidades principales de evaluación:

### 1. Modo "Construir Circuito" (Diseño Inverso)
A diferencia de los problemas de texto tradicionales, aquí se practica el **diseño guiado por especificaciones**:
- **Dinámica:** El simulador dictará un objetivo numérico aleatorio (Ej. *"Construye un circuito con $\omega_0 = 120$ rad/s y $\alpha = 45$ Np/s"*).
- **El reto:** El estudiante debe colocar una Resistencia, un Inductor y un Capacitor en el lienzo y calcular qué valores exactos en Ohmios, Henrios y Faradios permiten alcanzar esas frecuencias.
- **Gráfica en Tiempo Real:** Una vez completado, el estudiante puede visualizar la respuesta transitoria del circuito mediante `matplotlib`.

### 2. Modo "Análisis" (Evaluación Teórica)
Un banco de preguntas generadas aleatoriamente que evalúan la teoría analítica del estudiante sin necesidad de construir el circuito:
- **Adivinar el Comportamiento:** Dadas las frecuencias ($\omega_0$ y $\alpha$), elegir si es un circuito Subamortiguado, Sobreamortiguado o Críticamente amortiguado.
- **Cálculos Numéricos:** El sistema plantea un circuito con valores dados de R, L y C, y el estudiante debe calcular e ingresar manualmente el valor de $\omega_0$ o de $\alpha$.
- **Encontrar Componentes Faltantes:** Dado un $\omega_0$ objetivo y el valor de dos componentes (ej. el Inductor), el estudiante debe despejar y calcular el valor del Capacitor necesario.

---

## 🚀 Instalación y Ejecución

El proyecto está construido en Python puro utilizando **PyQt6** para la interfaz gráfica, y **numpy/matplotlib** para el motor matemático.

### Requisitos Previos
Asegúrate de tener Python 3.8+ instalado en tu sistema.

### Pasos para ejecutar
1. Clona o descarga el repositorio.
2. Abre una terminal (PowerShell, CMD o bash) en la carpeta del proyecto.
3. (Opcional pero recomendado) Activa el entorno virtual incluido:
   ```powershell
   .\venv\Scripts\activate
   ```
4. Instala las dependencias si aún no lo has hecho:
   ```bash
   pip install PyQt6 numpy matplotlib
   ```
5. ¡Lanza la aplicación!
   ```bash
   python app.py
   ```

---

*Proyecto desarrollado como herramienta didáctica para comprender de forma interactiva la teoría de sistemas amortiguados RLC.*
