import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math



root = tk.Tk()
root.title("Vector 2D / 3D Teaching Tool")

space_dim = tk.IntVar(master=root, value=2)

vectors = {}
entries = []

COLORS = ["blue", "red", "green", "purple", "orange", "brown", "pink", "cyan"]
color_index = 0


def get_next_color():
    global color_index
    c = COLORS[color_index % len(COLORS)]
    color_index += 1
    return c


def redraw():
    fig.clear()
    dim = space_dim.get()

    if dim == 2:
        ax = fig.add_subplot(111)
        ax.axhline(0)
        ax.axvline(0)
        ax.set_aspect("equal")
        ax.grid(True)
    else:
        ax = fig.add_subplot(111, projection="3d")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.scatter(0, 0, 0, s=50)
        ax.text(0, 0, 0, " O(0,0,0)")

    max_val = 1
    for v in vectors.values():
        if v["dim"] == dim:
            for c in v["value"]:
                max_val = max(max_val, abs(c))

    if dim == 2:
        ax.set_xlim(-max_val - 1, max_val + 1)
        ax.set_ylim(-max_val - 1, max_val + 1)
    else:
        ax.set_xlim(-max_val - 1, max_val + 1)
        ax.set_ylim(-max_val - 1, max_val + 1)
        ax.set_zlim(-max_val - 1, max_val + 1)

    for name, data in vectors.items():
        if data["dim"] != dim:
            continue

        v = data["value"]
        color = data["color"]

        if dim == 2:
            ax.quiver(0, 0, v[0], v[1],
                      angles="xy", scale_units="xy", scale=1, color=color)
            ax.text(v[0], v[1], f" {name}", color=color)
        else:
            ax.quiver(0, 0, 0, v[0], v[1], v[2],
                      color=color, arrow_length_ratio=0.1)
            ax.text(v[0], v[1], v[2], f" {name}", color=color)

    canvas.draw()

# Visualizer hay vãi

def add_vector():
    try:
        name = name_entry.get().strip()
        dim = space_dim.get()

        if dim == 2:
            x = float(x_entry.get())
            y = float(y_entry.get())
            value = (x, y)
            formula = f"{name} = ({x}, {y})"
        else:
            x = float(x_entry.get())
            y = float(y_entry.get())
            z = float(z_entry.get())
            value = (x, y, z)
            formula = f"{name} = ({x}, {y}, {z})"

        vectors[name] = {
            "value": value,
            "dim": dim,
            "color": get_next_color()
        }

        formula_label.config(text=formula)
        redraw()
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


def add_two_vectors():
    try:
        a = v1_entry.get().strip()
        b = v2_entry.get().strip()
        r = result_add_entry.get().strip()

        if vectors[a]["dim"] != vectors[b]["dim"]:
            raise ValueError("Không thể cộng vector khác chiều")

        dim = vectors[a]["dim"]
        va = vectors[a]["value"]
        vb = vectors[b]["value"]

        vr = tuple(va[i] + vb[i] for i in range(dim))

        vectors[r] = {
            "value": vr,
            "dim": dim,
            "color": get_next_color()
        }

        formula_label.config(
            text=f"{r} = {a} + {b} = {va} + {vb} = {vr}"
        )
        redraw()
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


def scale_vector():
    try:
        v = scale_vec_entry.get().strip()
        k = float(scale_entry.get())
        r = result_scale_entry.get().strip()

        vv = vectors[v]["value"]
        dim = vectors[v]["dim"]
        vr = tuple(k * c for c in vv)

        vectors[r] = {
            "value": vr,
            "dim": dim,
            "color": get_next_color()
        }

        formula_label.config(
            text=f"{r} = {k} × {v} = {k} × {vv} = {vr}"
        )
        redraw()
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


def vector_length():
    try:
        name = length_vec_entry.get().strip()

        if name not in vectors:
            raise ValueError("Vector không tồn tại")

        v = vectors[name]["value"]
        length = math.sqrt(sum(c * c for c in v))

        formula_label.config(
            text=f"‖{name}‖ = √({ ' + '.join(f'{c}²' for c in v) }) = {length:.4f}"
        )
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


def bind_entry(e):
    e.bind("<Return>", lambda _: focus_next(e))
    e.bind("<Down>", lambda _: focus_next(e))
    e.bind("<Up>", lambda _: focus_prev(e))


def focus_next(e):
    i = entries.index(e)
    if i < len(entries) - 1:
        entries[i + 1].focus()


def focus_prev(e):
    i = entries.index(e)
    if i > 0:
        entries[i - 1].focus()


def make_entry(parent, row, label):
    ttk.Label(parent, text=label).grid(row=row, column=0)
    e = ttk.Entry(parent, width=8)
    e.grid(row=row, column=1)
    bind_entry(e)
    entries.append(e)
    return e


left = ttk.Frame(root)
left.pack(side=tk.LEFT, padx=10, pady=10)

ttk.Label(left, text="Không gian").grid(row=0, column=0, columnspan=2)
ttk.Radiobutton(left, text="2D", variable=space_dim, value=2, command=redraw).grid(row=1, column=0)
ttk.Radiobutton(left, text="3D", variable=space_dim, value=3, command=redraw).grid(row=1, column=1)

ttk.Label(left, text="Nhập vector").grid(row=2, column=0, columnspan=2)

name_entry = make_entry(left, 3, "Tên")
x_entry = make_entry(left, 4, "x")
y_entry = make_entry(left, 5, "y")
z_entry = make_entry(left, 6, "z")

ttk.Button(left, text="Thêm vector", command=add_vector)\
    .grid(row=7, column=0, columnspan=2, pady=5)

ttk.Separator(left).grid(row=8, column=0, columnspan=2, sticky="ew", pady=8)

v1_entry = make_entry(left, 9, "Vector 1")
v2_entry = make_entry(left, 10, "Vector 2")
result_add_entry = make_entry(left, 11, "Kết quả")

ttk.Button(left, text="A + B", command=add_two_vectors)\
    .grid(row=12, column=0, columnspan=2)

ttk.Separator(left).grid(row=13, column=0, columnspan=2, sticky="ew", pady=8)

scale_vec_entry = make_entry(left, 14, "Vector")
scale_entry = make_entry(left, 15, "Scalar")
result_scale_entry = make_entry(left, 16, "Kết quả")

ttk.Button(left, text="k × V", command=scale_vector)\
    .grid(row=17, column=0, columnspan=2)

ttk.Separator(left).grid(row=18, column=0, columnspan=2, sticky="ew", pady=8)

length_vec_entry = make_entry(left, 19, "Vector")

ttk.Button(left, text="‖V‖", command=vector_length)\
    .grid(row=20, column=0, columnspan=2)

fig = plt.figure(figsize=(5, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

formula_label = ttk.Label(root, text="", wraplength=520, font=("Arial", 11))
formula_label.pack(side=tk.BOTTOM, pady=8)

redraw()
entries[0].focus()
root.mainloop()
    