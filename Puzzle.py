import sys
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QApplication, QMainWindow, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import QTimer
from algorithms import (
    bfs_solve, dfs, ids, ucs,
    greedy_best_first_search, ida_start, a_start,
    shc, steepest_ahc, stochastic_hc, simulated_annealing, beam_search, solution_for_ga,
    and_or_search,
    get_solution, min_conflicts,
    sensorless_solve_astar, solve_partial_observation_8puzzle
)
from sensorless import SensorlessApp
from partial_observation import PartialObs
from interface import ui_mainwindow

def manhattan_distance(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                goal_x, goal_y = divmod(state[i][j] - 1, 3)
                distance += abs(goal_x - i) + abs(goal_y - j)
    return distance

class EightPuzzleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 1. Load font SF Pro Display từ file
        font_id = QFontDatabase.addApplicationFont("fonts/SF-Pro-Display-Regular.otf")
        if font_id == -1:
            print("Không thể load font SF Pro Display!")
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                sf_pro_font = QFont(font_families[0])
                # 2. Đặt font cho toàn ứng dụng hoặc widget chính
                self.setFont(sf_pro_font)
            else:
                print("Không tìm thấy họ font sau khi load.")


        self.ui = ui_mainwindow()
        self.ui.setupUi(self) 

        # Set background app và font SF Pro Display
        self.setStyleSheet("""
            QWidget {
                background-color: #F9E6E4;
                font-family: 'SF Pro Display';
            }
        """)

        # In đậm "Đường đi:"
        self.ui.label_9.setStyleSheet("font-weight: bold;")

        # Đổi text và in đậm "Chọn thuật toán:" ➜ "Thuật toán:"
        self.ui.label.setText("Thuật toán:")
        self.ui.label.setStyleSheet("font-weight: bold;")

        # In đậm nút Sensorless và Partial Observation
        self.ui.sensorlessButton.setStyleSheet("font-weight: bold;")
        self.ui.parObButton.setStyleSheet("font-weight: bold;")

        self.ui.algorithmComboBox.setGeometry(QtCore.QRect(160, 20, 220, 31))
        self.ui.label_20.setGeometry(QtCore.QRect(400, 20, 81, 31))
        self.ui.timeLabel.setGeometry(QtCore.QRect(500, 20, 61, 31))


        # Style cho label số (background pastel hồng, bo góc, in đậm)
        label_style = """
            QLabel {
                background-color: #FFE5E7;
                border: 2px solid #FFB0B5;
                border-radius: 15px;
                font-weight: bold;
                font-size: 20px;
                color: #333333;
                qproperty-alignment: AlignCenter;
            }
        """
        for i in range(1, 9):
            label = getattr(self.ui, f"label_{i}", None)
            if label:
                label.setStyleSheet(label_style)
        if hasattr(self.ui, "label_empty"):
            self.ui.label_empty.setStyleSheet(label_style)
        for i in range(10, 19):
            label = getattr(self.ui, f"label_{i}", None)
            if label:
                label.setStyleSheet(label_style)

        # Style cho các nút với màu pastel và bo góc
        button_style = """
            QPushButton {
                background-color: #FFB0B5;
                border: none;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #FFC6CA;
            }
            QPushButton:pressed {
                background-color: #FFD3D6;
            }
        """
        for btn in [self.ui.solveButton, self.ui.resetButton, self.ui.exitButton, self.ui.sensorlessButton, self.ui.parObButton]:
            btn.setStyleSheet(button_style)

        self.ui.algorithmComboBox.setStyleSheet("""
            QComboBox {
                padding-right: 20px;
            }
        """)

        # Mở rộng kích thước cửa sổ để vừa bảng lịch sử
        self.resize(1200, 782)

        self.historyTable = QTableWidget(self.ui.centralwidget)
        self.historyTable.setColumnCount(3)
        self.historyTable.setHorizontalHeaderLabels(["Thuật toán", "Thời gian (s)", "Trạng thái"])
        self.historyTable.setGeometry(700, 60, 480, 700)
        self.historyTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.historyTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.historyTable.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.historyTable.setColumnWidth(0, 180)  # Thuật toán
        self.historyTable.setColumnWidth(1, 100)  # Thời gian
        self.historyTable.setColumnWidth(2, 120)  # Trạng thái
        self.historyTable.setStyleSheet("""
            QHeaderView::section {
                background-color: #FFC6CA;
                font-weight: bold;
            }
            QTableWidget {
                background-color: #FFE5E7;
                border: 1px solid #FFB0B5;
            }
        """)

        # Điều chỉnh label h(n)/f(n) và giá trị hiển thị
        self.ui.label_21.setGeometry(QtCore.QRect(470, 20, 40, 31))
        self.ui.hnLabel.setGeometry(QtCore.QRect(510, 20, 80, 31))

        # Tạo widget chứa 3 nút
        self.buttonColumnWidget = QWidget(self.ui.centralwidget)
        self.buttonColumnWidget.setGeometry(30, 80, 130, 120)  # chỉnh vị trí, kích thước phù hợp

        # Tạo layout dọc cho widget chứa nút
        vbox = QVBoxLayout(self.buttonColumnWidget)
        vbox.setSpacing(10)  # khoảng cách giữa các nút

        # Thêm nút vào layout
        vbox.addWidget(self.ui.solveButton)
        vbox.addWidget(self.ui.resetButton)
        vbox.addWidget(self.ui.exitButton)

        # Đặt kích thước cố định hoặc size policy cho từng nút để chúng đều nhau
        for btn in [self.ui.solveButton, self.ui.resetButton, self.ui.exitButton]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setMinimumHeight(30)
            btn.setMinimumWidth(120)

        # Giảm chiều cao bảng Đường đi, hạ sao cho cạnh dưới bằng cạnh dưới historyTable
        new_listwidget_height = 480  # cùng chiều cao với historyTable

        # Giảm chiều cao bảng Đường đi xuống 20 đơn vị
        listwidget_geo = self.ui.listWidget.geometry()
        new_height = listwidget_geo.height() - 20
        self.ui.listWidget.setGeometry(
            listwidget_geo.x(),
            listwidget_geo.y(),
            listwidget_geo.width(),
            new_height
        )

        # Đảm bảo listWidget có thanh cuộn dọc (QListWidget mặc định có thanh cuộn)
        self.ui.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Hạ cụm Mục tiêu xuống dưới bảng Đường đi (listWidget)
        label_target_geo = self.ui.label_19.geometry()
        new_label_target_y = self.ui.listWidget.geometry().y() + new_listwidget_height + 10
        self.ui.label_19.setGeometry(
            label_target_geo.x(),
            new_label_target_y,
            label_target_geo.width(),
            label_target_geo.height()
        )

        # Tính tọa độ Y mới cho 2 nút Sensorless và Partial Observation
        listwidget_geo = self.ui.listWidget.geometry()
        new_y = listwidget_geo.y() + listwidget_geo.height() + 10

        sensorless_geo = self.ui.sensorlessButton.geometry()
        self.ui.sensorlessButton.setGeometry(
            sensorless_geo.x(),
            new_y,
            sensorless_geo.width(),
            sensorless_geo.height()
        )

        partialob_geo = self.ui.parObButton.geometry()
        self.ui.parObButton.setGeometry(
            partialob_geo.x(),
            new_y,
            partialob_geo.width(),
            partialob_geo.height()
        )

        self.initial_state = [
            [2, 6, 5],
            [8, 0, 7],
            [4, 3, 1]
        ]    

        self.grid_labels = {}
        for i in range(3):
            for j in range(3):
                # Tên label dùng định dạng theo vị trí, ví dụ "label_2" với giá trị 2, "label_empty" với giá trị 0
                # Nhưng dễ nhất là bạn lưu label theo tọa độ i,j của ô:
                label_name = f"label_{i}_{j}"  # Bạn cần đổi tên label trong UI theo chuẩn này, hoặc map lại
                # Nếu UI chưa có label với tên đó, bạn phải map theo tên hiện tại:
                # Ví dụ label tên theo giá trị, thì map ngược:
                # label_value = self.initial_state[i][j]
                # label_name = f"label_{label_value}" if label_value != 0 else "label_empty"
                # Nhưng với update_grid, bạn muốn cập nhật text trên label theo vị trí i,j, nên tốt nhất đặt label theo tên i_j
                label = getattr(self.ui, label_name, None)
                if label:
                    self.grid_labels[(i, j)] = label
       

        # Khởi tạo positions mapping các label theo giá trị:
        self.positions = {}
        for i in range(3):
            for j in range(3):
                value = self.initial_state[i][j]
                label_name = f"label_{value}" if value != 0 else "label_empty"
                label = getattr(self.ui, label_name)
                self.positions[value] = label.pos()

        # Cập nhật giao diện với trạng thái mới ngay sau khi khởi tạo
        self.update_grid(self.initial_state)

        
        self.ui.solveButton.clicked.connect(self.solve_puzzle)
        self.ui.resetButton.clicked.connect(self.reset_puzzle)
        self.ui.exitButton.clicked.connect(self.close)
        self.ui.sensorlessButton.clicked.connect(self.open_sensorless_window)
        self.ui.parObButton.clicked.connect(self.open_partob_window)
        self.sensorless_window = None
        self.partial_obs_window = None 

    def open_partob_window(self):
        if self.partial_obs_window is None:
            self.partial_obs_window = PartialObs()
        self.partial_obs_window.show()

    def open_sensorless_window(self):
        if self.sensorless_window is None:
            self.sensorless_window = SensorlessApp()
        self.sensorless_window.show()

    def update_grid(self, state):
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                label_name = f"label_{value}" if value != 0 else "label_empty"
                if hasattr(self.ui, label_name):
                    label = getattr(self.ui, label_name)
                    new_x = self.positions[0].x() + j * 135
                    new_y = self.positions[0].y() + i * 125 
                    label.move(new_x, new_y)

    def solve_puzzle(self):
        QMessageBox.information(self, "Chú ý", "Đang tính toán tiến trình giải.")
        self.selected_algorithm = self.ui.algorithmComboBox.currentText()

        if self.selected_algorithm == "UCS":
            solution = ucs(self.initial_state)
        elif self.selected_algorithm == "BFS":
            solution = bfs_solve(self.initial_state)
        elif self.selected_algorithm == "IDS":
            solution = ids(self.initial_state)
        elif self.selected_algorithm == "DFS":
            solution = dfs(self.initial_state)
        elif self.selected_algorithm == "Greedy Search":
            solution = greedy_best_first_search(self.initial_state)
        elif self.selected_algorithm == "A* Search":
            solution = a_start(self.initial_state)
        elif self.selected_algorithm == "IDA* Search":
            solution = ida_start(self.initial_state)
        elif self.selected_algorithm == "Simple HC":
            solution = shc(self.initial_state)
        elif self.selected_algorithm == "Steepest Ascent HC":
            solution = steepest_ahc(self.initial_state)
        elif self.selected_algorithm == "Stochastic HC":
            solution = stochastic_hc(self.initial_state)
        elif self.selected_algorithm == "Simulated Annealing":
            solution = simulated_annealing(self.initial_state)
        elif self.selected_algorithm == "Beam Search":
            solution = beam_search(self.initial_state)
        elif self.selected_algorithm == "Genetic Algorithm":
            solution = solution_for_ga(self.initial_state)
        elif self.selected_algorithm == "AND-OR Graph":
            solution = and_or_search(self.initial_state)
        elif self.selected_algorithm == "Backtracking":
            solution = get_solution(self.initial_state, "Backtracking")
        elif self.selected_algorithm == "Backtracking with forward checking":
            solution = get_solution(self.initial_state, "Backtracking with forward checking")
        elif self.selected_algorithm == "Min-Conflicts":
            solution = min_conflicts(self.initial_state)
        else:
            solution = None

        self.solution = solution
        if self.solution:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_solution)
            self.solution_index = 0
            self.timer.start(300)
            self.start_time = time.time()
        else:
            QMessageBox.warning(self, "Thất bại", "Không tìm thấy lời giải!")
            row_pos = self.historyTable.rowCount()
            self.historyTable.insertRow(row_pos)
            self.historyTable.setItem(row_pos, 0, QTableWidgetItem(self.selected_algorithm))
            self.historyTable.setItem(row_pos, 1, QTableWidgetItem("-"))
            self.historyTable.setItem(row_pos, 2, QTableWidgetItem("Không giải được"))

    def update_solution(self):
        if self.solution_index < len(self.solution):
            self.initial_state = self.solution[self.solution_index]
            self.update_grid(self.initial_state)
            self.ui.listWidget.addItem(str(self.initial_state))
            h_n = manhattan_distance(self.initial_state)
            g_n = self.solution_index
            f_n = h_n + g_n
            if self.selected_algorithm == "Greedy Search":
                self.ui.label_21.setText("h(n) = ")
                self.ui.hnLabel.setText(str(h_n))
            elif self.selected_algorithm in ["A* Search", "IDA* Search"]:
                self.ui.label_21.setText("f(n) = ")
                self.ui.hnLabel.setText(str(f_n))
            self.solution_index += 1
        else:
            self.timer.stop()
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time
            self.ui.timeLabel.setText(f"{round(self.elapsed_time, 4)}s")
            QMessageBox.information(self, "Thành công", f"Thời gian thực hiện: {self.elapsed_time}s")
            row_pos = self.historyTable.rowCount()
            self.historyTable.insertRow(row_pos)
            self.historyTable.setItem(row_pos, 0, QTableWidgetItem(self.selected_algorithm))
            self.historyTable.setItem(row_pos, 1, QTableWidgetItem(f"{round(self.elapsed_time, 4)}"))
            self.historyTable.setItem(row_pos, 2, QTableWidgetItem("Thành công"))   

    def reset_puzzle(self):  
        self.initial_state = [
            [2, 6, 5],
            [8, 0, 7],
            [4, 3, 1]
        ]  
        self.update_grid(self.initial_state)
        self.ui.listWidget.clear()
        self.ui.timeLabel.clear()
        self.ui.hnLabel.clear()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    sf_font = QtGui.QFont("SF Pro Display")
    sf_font.setPointSize(10)
    app.setFont(sf_font)

    window = EightPuzzleApp()
    window.show()
    sys.exit(app.exec())
