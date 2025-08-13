from __future__ import annotations

from typing import List

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
)

from ..calculations import linear_fit
from ..plotting import MplCanvas


class CalibrationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = MplCanvas()

        self.table = QTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(["x (padrão)", "y (abs)"])

        self.fit_btn = QPushButton("Ajustar reta")
        self.fit_btn.clicked.connect(self._do_fit)

        self.clear_btn = QPushButton("Limpar")
        self.clear_btn.clicked.connect(self._clear)

        self.info = QLabel("")

        btns = QHBoxLayout()
        btns.addWidget(self.fit_btn)
        btns.addWidget(self.clear_btn)
        btns.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(btns)
        layout.addWidget(self.canvas)
        layout.addWidget(self.info)

    def _clear(self):
        self.table.clearContents()
        self.info.setText("")
        self.canvas.clear()

    def _do_fit(self):
        xs: List[float] = []
        ys: List[float] = []
        for r in range(self.table.rowCount()):
            x_item = self.table.item(r, 0)
            y_item = self.table.item(r, 1)
            try:
                if x_item is None or y_item is None:
                    continue
                x = float(x_item.text())
                y = float(y_item.text())
                xs.append(x)
                ys.append(y)
            except Exception:
                pass
        try:
            fit = linear_fit(xs, ys)
        except Exception as e:
            self.info.setText(f"Erro: {e}")
            return

        # plot
        ax = self.canvas.ax
        ax.clear()
        ax.scatter(xs, ys, label="dados")
        x_min, x_max = min(xs), max(xs)
        x_line = np.linspace(x_min, x_max, 100)
        y_line = fit.slope * x_line + fit.intercept
        ax.plot(x_line, y_line, 'r-', label=f"y = {fit.slope:.4g} x + {fit.intercept:.4g}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend()
        self.canvas.draw_idle()

        self.info.setText(f"r = {fit.r_value:.4f}, R² = {fit.r_squared:.4f}")
