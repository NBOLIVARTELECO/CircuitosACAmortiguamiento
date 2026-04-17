import sys
from PyQt6.QtWidgets import (QGraphicsItem, QGraphicsSceneMouseEvent, 
                             QInputDialog, QGraphicsTextItem)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont

class ComponentBase(QGraphicsItem):
    def __init__(self, name, unit, color):
        super().__init__()
        self.name = name
        self.unit = unit
        self.value = 0.0
        self.color = color
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Etiqueta de texto para mostrar nombre y valor
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPos(-20, 25)
        self.update_text()

    def update_text(self):
        self.text_item.setPlainText(f"{self.name}\n{self.value} {self.unit}")
        
    def boundingRect(self):
        return QRectF(-20, -20, 40, 40)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.GlobalColor.black, 2)
        if self.isSelected():
            pen.setColor(Qt.GlobalColor.red)
        
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(self.color)))
        
        # Dibuja un rectángulo genérico como base
        painter.drawRect(-20, -20, 40, 40)
        
        # Añade un texto central para identificar visualmente rápido
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.name)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        # Al hacer doble clic, pedir el valor al usuario
        value, ok = QInputDialog.getDouble(
            None, f"Valor de {self.name}", 
            f"Ingrese el valor en {self.unit}:", 
            self.value, 0, 1000000, 4
        )
        if ok:
            self.value = value
            self.update_text()
            # Emitir señal de actualización a la escena principal (lo manejaremos después)
            if self.scene():
                self.scene().update()
        super().mouseDoubleClickEvent(event)


class ResistorItem(ComponentBase):
    def __init__(self):
        super().__init__("R", "Ω", "#FFA07A") # Light salmon
        
    def paint(self, painter, option, widget):
        pen = QPen(Qt.GlobalColor.black, 2)
        if self.isSelected():
            pen.setColor(Qt.GlobalColor.red)
        painter.setPen(pen)
        
        # Dibujar un zigzag simple para la resistencia
        painter.drawLine(-20, 0, -10, -10)
        painter.drawLine(-10, -10, 0, 10)
        painter.drawLine(0, 10, 10, -10)
        painter.drawLine(10, -10, 20, 0)
        
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(-20, -20, 40, 20), Qt.AlignmentFlag.AlignCenter, "R")


class InductorItem(ComponentBase):
    def __init__(self):
        super().__init__("L", "H", "#98FB98") # Pale green
        
    def paint(self, painter, option, widget):
        pen = QPen(Qt.GlobalColor.black, 2)
        if self.isSelected():
            pen.setColor(Qt.GlobalColor.red)
        painter.setPen(pen)
        
        # Dibujar bucles para el inductor
        painter.drawArc(-20, -10, 10, 20, 0, 180 * 16)
        painter.drawArc(-10, -10, 10, 20, 0, 180 * 16)
        painter.drawArc(0, -10, 10, 20, 0, 180 * 16)
        painter.drawArc(10, -10, 10, 20, 0, 180 * 16)
        
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(-20, -20, 40, 10), Qt.AlignmentFlag.AlignCenter, "L")


class CapacitorItem(ComponentBase):
    def __init__(self):
        super().__init__("C", "F", "#87CEFA") # Light sky blue
        
    def paint(self, painter, option, widget):
        pen = QPen(Qt.GlobalColor.black, 2)
        if self.isSelected():
            pen.setColor(Qt.GlobalColor.red)
        painter.setPen(pen)
        
        # Dibujar placas paralelas para el capacitor
        painter.drawLine(-5, -15, -5, 15)
        painter.drawLine(5, -15, 5, 15)
        # Hilos conectores
        painter.drawLine(-20, 0, -5, 0)
        painter.drawLine(5, 0, 20, 0)
        
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(-20, -20, 40, 10), Qt.AlignmentFlag.AlignCenter, "C")
