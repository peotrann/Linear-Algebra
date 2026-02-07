import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

root = tk.Tk()
root.title("Vector Span Visualizer")

# Thiết lập kích thước cửa sổ lớn hơn
root.geometry("1100x700")

space_dim = tk.IntVar(value=2)
show_result = tk.BooleanVar(value=True)
show_random_vectors = tk.BooleanVar(value=True)
show_span = tk.BooleanVar(value=False)
show_independence_result = tk.BooleanVar(value=False)  # Biến mới cho hiển thị kết quả

vectors = {}
sliders = {}
entries = []
random_vectors = []
independence_result_text = ""  # Lưu kết quả kiểm tra

VECTOR_COLORS = ["blue", "green", "purple"]
# CẢI THIỆN: Màu sắc rõ ràng hơn cho span
SPAN_COLORS = {
    "point": [1.0, 0.0, 0.0, 0.3],      # Đỏ - điểm
    "line": [0.0, 0.8, 0.0, 0.4],       # Xanh lá - đường thẳng
    "plane": [0.0, 0.6, 1.0, 0.1],      # Xanh dương - mặt phẳng (giảm alpha)
    "space": [0.6, 0.0, 0.8, 0.05]      # Tím - không gian (giảm alpha)
}


def default_vectors():
    """Đặt lại vector cơ sở về giá trị mặc định"""
    vectors.clear()
    dim = space_dim.get()

    if dim == 2:
        vectors["v1"] = [1.0, 0.0]
        vectors["v2"] = [0.0, 1.0]
    else:
        vectors["v1"] = [1.0, 0.0, 0.0]
        vectors["v2"] = [0.0, 1.0, 0.0]
        vectors["v3"] = [0.0, 0.0, 1.0]
    
    # Đặt lại slider về 1
    for name in sliders:
        sliders[name].set(1)
    
    # Đặt lại các ô nhập liệu về giá trị mặc định
    reset_entry_values()


def reset_entry_values():
    """Đặt lại giá trị của các ô nhập vector"""
    for entry in entries:
        entry.destroy()
    entries.clear()
    
    dim = space_dim.get()
    for i, name in enumerate(vectors):
        for j in range(dim):
            e = ttk.Entry(vector_frame, width=8)  # Tăng width từ 6 lên 8
            e.insert(0, str(vectors[name][j]))
            e.grid(row=i, column=j + 1, padx=2)
            e.bind("<KeyRelease>",
                  lambda ev, n=name, idx=j, ent=e: update_vector(n, idx, ent.get()))
            e.bind("<Return>", focus_next)
            entries.append(e)
    
    if entries:
        entries[0].focus_set()


def reset_all():
    """Reset toàn bộ về trạng thái ban đầu"""
    default_vectors()
    random_vectors.clear()
    independence_result_text = ""
    show_independence_result.set(False)
    redraw()


def generate_random_vectors():
    random_vectors.clear()
    dim = space_dim.get()
    
    if dim == 2:
        for _ in range(20):
            a = random.uniform(-3, 3)
            b = random.uniform(-3, 3)
            v1 = vectors["v1"]
            v2 = vectors["v2"]
            vec = [a * v1[0] + b * v2[0], a * v1[1] + b * v2[1]]
            random_vectors.append(vec)
    else:
        for _ in range(15):  # Giảm số lượng vector ngẫu nhiên để giảm lag
            a = random.uniform(-2, 2)
            b = random.uniform(-2, 2)
            c = random.uniform(-2, 2)
            v1 = vectors["v1"]
            v2 = vectors["v2"]
            v3 = vectors["v3"]
            vec = [
                a * v1[0] + b * v2[0] + c * v3[0],
                a * v1[1] + b * v2[1] + c * v3[1],
                a * v1[2] + b * v2[2] + c * v3[2]
            ]
            random_vectors.append(vec)
    
    redraw()


def check_linear_independence():
    """Kiểm tra tính độc lập/phụ thuộc tuyến tính của các vector"""
    global independence_result_text
    dim = space_dim.get()
    
    if dim == 2:
        v1 = np.array(vectors["v1"])
        v2 = np.array(vectors["v2"])
        
        # Tạo ma trận từ các vector
        if len(v1) == 2:
            A = np.array([v1, v2])
        else:
            A = np.array([v1, v2]).T  # Chuyển vị nếu cần
        
        # Tính hạng của ma trận
        rank = np.linalg.matrix_rank(A)
        
        if rank == 2:
            independence_result_text = (
                "Cac vector DOC LAP tuyen tinh\n\n"
                f"Vector v1: ({v1[0]:.2f}, {v1[1]:.2f})\n"
                f"Vector v2: ({v2[0]:.2f}, {v2[1]:.2f})\n\n"
                f"Hang ma tran: {rank}/2"
            )
        else:
            independence_result_text = (
                "Cac vector PHU THUOC tuyen tinh\n\n"
                f"Vector v1: ({v1[0]:.2f}, {v1[1]:.2f})\n"
                f"Vector v2: ({v2[0]:.2f}, {v2[1]:.2f})\n\n"
                f"Hang ma tran: {rank}/2"
            )
    
    else:  # 3D
        v1 = np.array(vectors["v1"])
        v2 = np.array(vectors["v2"])
        v3 = np.array(vectors["v3"])
        
        # Tạo ma trận từ các vector
        A = np.array([v1, v2, v3])
        
        # Tính hạng của ma trận
        rank = np.linalg.matrix_rank(A)
        
        if rank == 3:
            independence_result_text = (
                "Cac vector DOC LAP tuyen tinh\n\n"
                f"v1: ({v1[0]:.2f}, {v1[1]:.2f}, {v1[2]:.2f})\n"
                f"v2: ({v2[0]:.2f}, {v2[1]:.2f}, {v2[2]:.2f})\n"
                f"v3: ({v3[0]:.2f}, {v3[1]:.2f}, {v3[2]:.2f})\n\n"
                f"Hang ma tran: {rank}/3"
            )
        elif rank == 2:
            independence_result_text = (
                "Cac vector PHU THUOC tuyen tinh\n\n"
                f"v1: ({v1[0]:.2f}, {v1[1]:.2f}, {v1[2]:.2f})\n"
                f"v2: ({v2[0]:.2f}, {v2[1]:.2f}, {v2[2]:.2f})\n"
                f"v3: ({v3[0]:.2f}, {v3[1]:.2f}, {v3[2]:.2f})\n\n"
                f"Hang ma tran: {rank}/3\n"
                f"Cac vector nam tren mot mat phang"
            )
        elif rank == 1:
            independence_result_text = (
                "Cac vector PHU THUOC tuyen tinh\n\n"
                f"v1: ({v1[0]:.2f}, {v1[1]:.2f}, {v1[2]:.2f})\n"
                f"v2: ({v2[0]:.2f}, {v2[1]:.2f}, {v2[2]:.2f})\n"
                f"v3: ({v3[0]:.2f}, {v3[1]:.2f}, {v3[2]:.2f})\n\n"
                f"Hang ma tran: {rank}/3\n"
                f"Cac vector nam tren mot duong thang"
            )
        else:  # rank = 0
            independence_result_text = (
                "Tat ca cac vector deu la vector 0\n\n"
                f"v1: ({v1[0]:.2f}, {v1[1]:.2f}, {v1[2]:.2f})\n"
                f"v2: ({v2[0]:.2f}, {v2[1]:.2f}, {v2[2]:.2f})\n"
                f"v3: ({v3[0]:.2f}, {v3[1]:.2f}, {v3[2]:.2f})\n\n"
                f"Hang ma tran: {rank}/3"
            )
    
    # Hiển thị kết quả
    show_independence_result.set(True)
    redraw()


def calculate_span_area_2d(v1, v2):
    """Tính diện tích hình bình hành tạo bởi 2 vector"""
    return abs(v1[0]*v2[1] - v1[1]*v2[0])


def create_cube(ax, center, size, color, alpha):
    """Tạo hình lập phương để biểu diễn không gian"""
    # Các đỉnh của hình lập phương
    r = size / 2
    vertices = np.array([
        [center[0]-r, center[1]-r, center[2]-r],
        [center[0]+r, center[1]-r, center[2]-r],
        [center[0]+r, center[1]+r, center[2]-r],
        [center[0]-r, center[1]+r, center[2]-r],
        [center[0]-r, center[1]-r, center[2]+r],
        [center[0]+r, center[1]-r, center[2]+r],
        [center[0]+r, center[1]+r, center[2]+r],
        [center[0]-r, center[1]+r, center[2]+r]
    ])
    
    # Các mặt của hình lập phương
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]], 
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[4], vertices[7], vertices[3], vertices[0]]
    ]
    
    # Vẽ hình lập phương
    cube = Poly3DCollection(faces, alpha=alpha, facecolors=color, 
                           linewidths=0.5, edgecolors=[c*0.7 for c in color[:3]])
    ax.add_collection3d(cube)


def visualize_span(ax, dim):
    if not show_span.get():
        return None  # Trả về None nếu không hiển thị span
    
    if dim == 2:
        v1 = np.array(vectors["v1"])
        v2 = np.array(vectors["v2"])
        
        # Kiểm tra độ phụ thuộc tuyến tính
        area = calculate_span_area_2d(v1, v2)
        
        if area < 1e-10:  # Phụ thuộc tuyến tính (1 chiều)
            # Chọn vector khác 0
            if np.linalg.norm(v1) > 1e-10:
                dir_vec = v1
            else:
                dir_vec = v2
            
            # Chuẩn hóa vector
            norm = np.linalg.norm(dir_vec)
            if norm > 0:
                dir_vec = dir_vec / norm
            
            # Vẽ đường thẳng
            t = np.linspace(-7, 7, 2)
            x = t * dir_vec[0]
            y = t * dir_vec[1]
            ax.plot(x, y, color=SPAN_COLORS["line"], linewidth=4,
                   label="Span (đường thẳng)")
            return "line"
        else:  # Độc lập tuyến tính (2 chiều - mặt phẳng)
            # TÔ MÀU TOÀN BỘ ĐỒ THỊ 2D MÀU XANH MỜ
            # Tạo một hình chữ nhật lớn che phủ toàn bộ đồ thị
            x_min, x_max = -5, 5
            y_min, y_max = -5, 5
            
            # Vẽ hình chữ nhật lớn tô màu xanh mờ
            rect = plt.Rectangle((x_min, y_min), 
                                x_max - x_min, 
                                y_max - y_min, 
                                facecolor=SPAN_COLORS["plane"], 
                                edgecolor='none',
                                zorder=1,
                                label="Span (mặt phẳng)")
            ax.add_patch(rect)
            
            # Thêm đường viền để dễ nhận biết
            ax.plot([x_min, x_max, x_max, x_min, x_min], 
                   [y_min, y_min, y_max, y_max, y_min], 
                   'b-', alpha=0.3, linewidth=2, zorder=2)
            
            return "plane"
    
    else:  # 3D
        v1 = np.array(vectors["v1"])
        v2 = np.array(vectors["v2"])
        v3 = np.array(vectors["v3"])
        
        matrix = np.array([v1, v2, v3])
        rank = np.linalg.matrix_rank(matrix)
        
        if rank == 1:  # Đường thẳng
            # Chọn vector khác 0
            for vec in [v1, v2, v3]:
                if np.linalg.norm(vec) > 1e-10:
                    dir_vec = vec
                    break
            
            # Chuẩn hóa
            norm = np.linalg.norm(dir_vec)
            if norm > 0:
                dir_vec = dir_vec / norm
            
            # Vẽ đường thẳng
            t = np.linspace(-7, 7, 2)
            x = t * dir_vec[0]
            y = t * dir_vec[1]
            z = t * dir_vec[2]
            
            ax.plot(x, y, z, 
                   color=SPAN_COLORS["line"], alpha=0.8, linewidth=4,
                   label="Span (đường thẳng)")
            return "line"
        
        elif rank == 2:  # Mặt phẳng
            # Tìm 2 vector độc lập
            u1 = v1 / np.linalg.norm(v1) if np.linalg.norm(v1) > 0 else v1
            
            # Loại bỏ thành phần của v2 theo hướng u1
            v2_proj = v2 - np.dot(v2, u1) * u1
            if np.linalg.norm(v2_proj) > 1e-10:
                u2 = v2_proj / np.linalg.norm(v2_proj)
            else:
                # Thử với v3
                v3_proj = v3 - np.dot(v3, u1) * u1
                if np.linalg.norm(v3_proj) > 1e-10:
                    u2 = v3_proj / np.linalg.norm(v3_proj)
                else:
                    u2 = np.array([0, 0, 1])  # Fallback
            
            # Tạo lưới cho mặt phẳng
            s = np.linspace(-3, 3, 15)  # Giảm độ phân giải
            t = np.linspace(-3, 3, 15)
            S, T = np.meshgrid(s, t)
            
            # Tạo các điểm trên mặt phẳng
            X = S * u1[0] + T * u2[0]
            Y = S * u1[1] + T * u2[1]
            Z = S * u1[2] + T * u2[2]
            
            # Vẽ mặt phẳng
            ax.plot_surface(X, Y, Z, 
                          color=SPAN_COLORS["plane"][:3], 
                          alpha=0.25,
                          rstride=1, cstride=1,
                          linewidth=0,
                          antialiased=False,
                          shade=False,
                          label="Span (mặt phẳng)")
            return "plane"
        
        elif rank == 3:  # Toàn bộ không gian 3D
            # Sử dụng hình lập phương để biểu diễn không gian 3D
            create_cube(ax, [0, 0, 0], 10, SPAN_COLORS["space"], 0.08)
            return "space"
    
    return None


def build_formula():
    terms = []
    for name in vectors:
        k = sliders[name].get()
        terms.append(f"{k:.1f}{name}")
    return "r = " + " + ".join(terms)


def redraw():
    fig.clear()
    dim = space_dim.get()

    if dim == 2:
        ax = fig.add_subplot(111)
        ax.axhline(0, color='gray', linewidth=0.5, alpha=0.5)
        ax.axvline(0, color='gray', linewidth=0.5, alpha=0.5)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_xlabel("X", fontsize=10)
        ax.set_ylabel("Y", fontsize=10)
    else:
        ax = fig.add_subplot(111, projection="3d")
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_zlim(-5, 5)
        ax.set_xlabel("X", fontsize=9)
        ax.set_ylabel("Y", fontsize=9)
        ax.set_zlabel("Z", fontsize=9)
        ax.xaxis.set_pane_color((0.95, 0.95, 0.95, 0.05))
        ax.yaxis.set_pane_color((0.95, 0.95, 0.95, 0.05))
        ax.zaxis.set_pane_color((0.95, 0.95, 0.95, 0.05))

    # Vẽ span và lấy loại span
    span_type = visualize_span(ax, dim)

    result = [0] * dim

    # Vẽ các vector cơ sở
    for i, (name, vec) in enumerate(vectors.items()):
        k = sliders[name].get()
        scaled = [k * c for c in vec]

        for j in range(dim):
            result[j] += scaled[j]

        color = VECTOR_COLORS[i % len(VECTOR_COLORS)]

        if dim == 2:
            ax.quiver(0, 0, scaled[0], scaled[1],
                     angles="xy", scale_units="xy", scale=1, 
                     color=color, width=0.003,
                     headwidth=4, headlength=5, headaxislength=4.5,
                     minlength=0.1, zorder=10)
            offset_x = scaled[0] * 0.1
            offset_y = scaled[1] * 0.1
            ax.text(scaled[0] + offset_x, scaled[1] + offset_y, 
                   f"{k:.1f}{name}", color=color, fontsize=8,
                   bbox=dict(boxstyle="round,pad=0.2", 
                            facecolor="white", 
                            alpha=0.8, 
                            edgecolor="lightgray"),
                   zorder=10)
        else:
            ax.quiver(0, 0, 0, scaled[0], scaled[1], scaled[2], 
                     color=color, linewidth=1.5, arrow_length_ratio=0.1)
            ax.text(scaled[0], scaled[1], scaled[2], 
                   f"{k:.1f}{name}", color=color, fontsize=7,
                   bbox=dict(boxstyle="round,pad=0.2", 
                            facecolor="white", 
                            alpha=0.8, 
                            edgecolor="lightgray"),
                   zorder=10)

    # Vẽ các vector ngẫu nhiên với màu sắc rõ ràng hơn
    if show_random_vectors.get() and random_vectors:
        if dim == 2:
            for vec in random_vectors:
                ax.quiver(0, 0, vec[0], vec[1],
                         angles="xy", scale_units="xy", scale=1,
                         color='orange', alpha=0.7, width=0.002,
                         headwidth=3, headlength=4, headaxislength=3.5,
                         zorder=5)
                ax.scatter(vec[0], vec[1], color='orange', 
                          alpha=0.6, s=15, marker='o', zorder=5)
        else:
            # Giới hạn số lượng vector hiển thị để giảm lag
            display_vectors = random_vectors[:10]  # Chỉ hiển thị 10 vector
            for vec in display_vectors:
                ax.quiver(0, 0, 0, vec[0], vec[1], vec[2],
                         color='orange', alpha=0.7, linewidth=1,
                         arrow_length_ratio=0.08, zorder=5)
                ax.scatter([vec[0]], [vec[1]], [vec[2]], 
                          color='orange', alpha=0.6, s=20, marker='o', zorder=5)

    # Vẽ vector tổng
    if show_result.get():
        formula = build_formula()
        if dim == 2:
            ax.quiver(0, 0, result[0], result[1],
                     angles="xy", scale_units="xy", scale=1, 
                     color="red", width=0.004,
                     headwidth=5, headlength=6, headaxislength=5.5,
                     zorder=15)
            ax.text(result[0], result[1], formula, color="red", 
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", 
                            facecolor="white", 
                            alpha=0.9, 
                            edgecolor="red"),
                   zorder=15)
        else:
            ax.quiver(0, 0, 0, result[0], result[1], result[2], 
                     color="red", linewidth=2, arrow_length_ratio=0.12,
                     zorder=15)
            ax.text(result[0], result[1], result[2], formula, 
                   color="red", fontsize=8, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", 
                            facecolor="white", 
                            alpha=0.9, 
                            edgecolor="red"),
                   zorder=15)

    # HIỂN THỊ KẾT QUẢ KIỂM TRA ĐỘC LẬP TUYẾN TÍNH
    if show_independence_result.get() and independence_result_text:
        # Tạo một textbox để hiển thị kết quả
        if dim == 2:
            # Hiển thị ở góc trên bên trái cho 2D
            props = dict(boxstyle='round', facecolor='lightyellow', 
                        alpha=0.95, edgecolor='gold', linewidth=2)
            ax.text(0.02, 0.98, independence_result_text, 
                   transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', bbox=props,
                   fontfamily='monospace')
        else:
            # Hiển thị ở góc dưới bên phải cho 3D
            props = dict(boxstyle='round', facecolor='lightyellow', 
                        alpha=0.95, edgecolor='gold', linewidth=2)
            ax.text2D(0.98, 0.02, independence_result_text, 
                     transform=ax.transAxes, fontsize=9,
                     verticalalignment='bottom', horizontalalignment='right',
                     bbox=props, fontfamily='monospace')

    # Thêm legend với màu sắc rõ ràng
    legend_handles = []
    legend_labels = []
    
    if show_span.get() and span_type:
        # Thêm span vào legend với màu tương ứng
        if span_type == "line":
            color = SPAN_COLORS["line"]
            label = "Span (đường thẳng)"
        elif span_type == "plane":
            color = SPAN_COLORS["plane"]
            label = "Span (mặt phẳng)"
        elif span_type == "space":
            color = SPAN_COLORS["space"]
            label = "Span (không gian 3D)"
        else:
            color = [0.5, 0.5, 0.5, 0.5]
            label = "Span"
        
        if dim == 2:
            legend_handles.append(plt.Line2D([0], [0], color=color, linewidth=10))
        else:
            legend_handles.append(plt.Line2D([0], [0], color=color, linewidth=10))
        legend_labels.append(label)
    
    if show_random_vectors.get() and random_vectors:
        # Vector ngẫu nhiên với màu cam đậm
        legend_handles.append(plt.Line2D([0], [0], color='orange', alpha=0.7, linewidth=2))
        legend_labels.append("Vector ngẫu nhiên")
    
    # Vector tổng
    if show_result.get():
        legend_handles.append(plt.Line2D([0], [0], color='red', linewidth=2))
        legend_labels.append("Vector tổng")
    
    if legend_handles:
        ax.legend(legend_handles, legend_labels, loc='upper right', fontsize=8,
                 framealpha=0.95, facecolor='white', edgecolor='gray')

    canvas.draw()


def update_vector(name, idx, value):
    try:
        vectors[name][idx] = float(value)
        redraw()
    except ValueError:
        pass


def focus_next(event):
    try:
        idx = entries.index(event.widget)
        if idx + 1 < len(entries):
            entries[idx + 1].focus_set()
    except ValueError:
        pass
    return "break"


def switch_space_dimension():
    """Chuyển đổi giữa 2D và 3D - LUÔN RESET VỀ VECTOR CƠ SỞ"""
    # Reset tất cả về mặc định
    show_span.set(False)  # Tắt span khi chuyển đổi
    show_independence_result.set(False)  # Ẩn kết quả kiểm tra
    random_vectors.clear()  # Xóa vector ngẫu nhiên
    
    # Xóa các widget cũ
    for w in vector_frame.winfo_children():
        w.destroy()
    for w in slider_frame.winfo_children():
        w.destroy()
    
    sliders.clear()
    entries.clear()
    
    # Đặt lại vector cơ sở
    default_vectors()
    
    # Xây dựng lại UI với vector mặc định
    dim = space_dim.get()

    for i, name in enumerate(vectors):
        ttk.Label(vector_frame, text=name).grid(row=i, column=0, padx=3)

        for j in range(dim):
            e = ttk.Entry(vector_frame, width=8)  # Tăng width từ 6 lên 8
            e.insert(0, str(vectors[name][j]))
            e.grid(row=i, column=j + 1, padx=2)
            e.bind("<KeyRelease>",
                  lambda ev, n=name, idx=j, ent=e: update_vector(n, idx, ent.get()))
            e.bind("<Return>", focus_next)
            entries.append(e)

        s = tk.Scale(
            slider_frame,
            from_=-5,
            to=5,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            length=200,
            command=lambda e: redraw()
        )
        s.set(1)
        s.pack(anchor="w", pady=2)
        sliders[name] = s

    if entries:
        entries[0].focus_set()
    
    # Vẽ lại đồ thị
    redraw()


def rebuild_ui():
    """Xây dựng lại UI - LUÔN RESET VỀ VECTOR CƠ SỞ"""
    switch_space_dimension()


# Tạo giao diện với Frame lớn hơn
control = ttk.Frame(root, width=300)
control.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Tạo một canvas để có thể cuộn nếu cần
canvas_control = tk.Canvas(control)
scrollbar = ttk.Scrollbar(control, orient="vertical", command=canvas_control.yview)
scrollable_frame = ttk.Frame(canvas_control)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas_control.configure(scrollregion=canvas_control.bbox("all"))
)

canvas_control.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas_control.configure(yscrollcommand=scrollbar.set)

# Đóng gói canvas và scrollbar
canvas_control.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Bây giờ sử dụng scrollable_frame thay vì control
ttk.Label(scrollable_frame, text="Không gian", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))

# Sửa lại radiobutton để gọi switch_space_dimension thay vì rebuild_ui trực tiếp
ttk.Radiobutton(scrollable_frame, text="2D", variable=space_dim,
               value=2, command=switch_space_dimension).pack(anchor="w")
ttk.Radiobutton(scrollable_frame, text="3D", variable=space_dim,
               value=3, command=switch_space_dimension).pack(anchor="w")

ttk.Separator(scrollable_frame).pack(fill="x", pady=10)

ttk.Label(scrollable_frame, text="Vector cơ sở", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))

vector_frame = ttk.Frame(scrollable_frame)
vector_frame.pack(anchor="w")

ttk.Label(scrollable_frame, text="Hệ số", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))

slider_frame = ttk.Frame(scrollable_frame)
slider_frame.pack(anchor="w")

ttk.Separator(scrollable_frame).pack(fill="x", pady=10)

# Tạo frame cho các nút với chiều rộng cố định
button_frame = ttk.Frame(scrollable_frame)
button_frame.pack(anchor="w", fill=tk.X, pady=5)

# Nút Reset - CẢI THIỆN: Reset cả vector cơ sở và giá trị nhập
reset_btn = ttk.Button(button_frame, text="Reset Vector Cơ Sở", 
                      command=reset_all, width=25)
reset_btn.pack(anchor="w", pady=2)

# NÚT MỚI: Kiểm tra độc lập tuyến tính
check_independence_btn = ttk.Button(button_frame, text="Kiểm tra Độc lập Tuyến tính",
                                   command=check_linear_independence, width=25)
check_independence_btn.pack(anchor="w", pady=2)

# Nút tạo vector ngẫu nhiên
random_btn = ttk.Button(button_frame, text="Tạo Vector Ngẫu Nhiên", 
                       command=generate_random_vectors, width=25)
random_btn.pack(anchor="w", pady=2)

# Checkbutton hiển thị vector ngẫu nhiên
random_check = ttk.Checkbutton(scrollable_frame, text="Hiện Vector Ngẫu Nhiên",
                              variable=show_random_vectors, command=redraw)
random_check.pack(anchor="w", pady=5)

# Checkbutton hiển thị span
span_check = ttk.Checkbutton(scrollable_frame, text="Hiển Thị Span (Không gian con)",
                            variable=show_span, command=redraw)
span_check.pack(anchor="w", pady=5)

# Checkbutton hiển thị kết quả kiểm tra độc lập
independence_check = ttk.Checkbutton(scrollable_frame, text="Hiển Thị Kết Quả Kiểm Tra",
                                    variable=show_independence_result, command=redraw)
independence_check.pack(anchor="w", pady=5)

ttk.Separator(scrollable_frame).pack(fill="x", pady=10)

# Checkbutton hiển thị vector tổng
result_check = ttk.Checkbutton(scrollable_frame, text="Hiện Vector Tổng",
                              variable=show_result, command=redraw)
result_check.pack(anchor="w", pady=5)

# Thêm chú thích về màu sắc
ttk.Separator(scrollable_frame).pack(fill="x", pady=10)
ttk.Label(scrollable_frame, text="Chú thích màu sắc:", 
         font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))

color_info = ttk.Frame(scrollable_frame)
color_info.pack(anchor="w", pady=5)

# Hiển thị màu span
colors_frame = ttk.Frame(color_info)
colors_frame.pack(anchor="w")

span_colors_text = [
    ("• Đường thẳng:", "Xanh lá", SPAN_COLORS["line"]),
    ("• Mặt phẳng:", "Xanh dương", SPAN_COLORS["plane"]),
    ("• Không gian 3D:", "Tím", SPAN_COLORS["space"]),
    ("• Vector ngẫu nhiên:", "Cam", [1.0, 0.5, 0.0, 1.0]),
    ("• Vector tổng:", "Đỏ", [1.0, 0.0, 0.0, 1.0])
]

for i, (desc, name, color_rgba) in enumerate(span_colors_text):
    color_display = tk.Canvas(colors_frame, width=15, height=15, bg='white', 
                             highlightthickness=1, highlightbackground="gray")
    color_display.create_rectangle(2, 2, 13, 13, 
                                  fill='#%02x%02x%02x' % (int(color_rgba[0]*255), 
                                                         int(color_rgba[1]*255), 
                                                         int(color_rgba[2]*255)))
    color_display.grid(row=i, column=0, padx=(0, 5), pady=1, sticky='w')
    
    ttk.Label(colors_frame, text=f"{desc} {name}", font=("Arial", 8)).grid(
        row=i, column=1, sticky='w', pady=1)

# Thêm thông tin
ttk.Separator(scrollable_frame).pack(fill="x", pady=10)
ttk.Label(scrollable_frame, text="Lưu ý:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
ttk.Label(scrollable_frame, text="• Khi chuyển 2D/3D sẽ tự động reset", 
         font=("Arial", 8)).pack(anchor="w")
ttk.Label(scrollable_frame, text="• Span sẽ tự động tắt khi chuyển", 
         font=("Arial", 8)).pack(anchor="w")
ttk.Label(scrollable_frame, text="• Vector ngẫu nhiên sẽ bị xóa", 
         font=("Arial", 8)).pack(anchor="w")

# Tạo figure cho đồ thị
fig = plt.figure(figsize=(7, 6), dpi=90)  # Tăng kích thước figure
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Khởi tạo giao diện
switch_space_dimension()  # Sử dụng hàm mới để khởi tạo

# Chạy ứng dụng
root.mainloop()