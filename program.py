import tkinter as tk
from tkinter import colorchooser, ttk, filedialog, messagebox
import json
import math

class ShapeDrawer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Shape Drawer")
        self.geometry("800x600")

        self.selected_shape = tk.StringVar(value="Point")
        self.color = "#000000"
        self.shapes = []
        self.mode = tk.StringVar(value="Draw")
        
        self.create_widgets()
        
        self.start_x = None
        self.start_y = None
        self.current_shape_id = None
        self.moving_shape = False
        self.rotating_shape = False
        self.resizing_shape = False
        self.control_point_ids = []

    def create_widgets(self):
        control_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self, bg="white", width=600, height=600)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        shapes_label = tk.Label(control_frame, text="Shape:")
        shapes_label.pack(pady=5)

        shapes_dropdown = ttk.Combobox(control_frame, textvariable=self.selected_shape, values=["Point", "Line", "Circle", "Square", "Triangle", "Octagon"])
        shapes_dropdown.pack(pady=5)

        color_button = tk.Button(control_frame, text="Choose Color", command=self.choose_color)
        color_button.pack(pady=5)

        clear_button = tk.Button(control_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_button.pack(pady=5)

        save_button = tk.Button(control_frame, text="Save", command=self.save_canvas)
        save_button.pack(pady=5)

        load_button = tk.Button(control_frame, text="Load", command=self.load_canvas)
        load_button.pack(pady=5)

        mode_button = tk.Button(control_frame, text="Toggle Mode", command=self.toggle_mode)
        mode_button.pack(pady=5)

        self.status_label = tk.Label(control_frame, text="Status: Ready")
        self.status_label.pack(pady=5)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose color")
        if color_code:
            self.color = color_code[1]

    def clear_canvas(self):
        self.canvas.delete("all")
        self.shapes.clear()
        
    def save_canvas(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            shapes_data = [
                {
                    "type": shape["type"],
                    "coords": self.canvas.coords(shape["id"]),
                    "color": self.canvas.itemcget(shape["id"], "outline"),
                    "fill": self.canvas.itemcget(shape["id"], "fill")
                } for shape in self.shapes
            ]
            with open(file_path, 'w') as f:
                json.dump(shapes_data, f)
            self.status_label.config(text="Status: Canvas saved")

    def load_canvas(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                shapes_data = json.load(f)
            self.clear_canvas()
            for shape in shapes_data:
                self.color = shape["color"]
                fill_color = shape["fill"]
                if shape["type"] == "Point":
                    self.draw_point(*shape["coords"], self.color, fill_color, save=False)
                elif shape["type"] == "Line":
                    self.draw_line(*shape["coords"], self.color, save=False)
                elif shape["type"] == "Circle":
                    self.draw_circle(*shape["coords"], self.color, fill_color, save=False)
                elif shape["type"] == "Square":
                    self.draw_square(*shape["coords"], self.color, fill_color, save=False)
                elif shape["type"] == "Triangle":
                    self.draw_triangle(*shape["coords"], self.color, fill_color, save=False)
                elif shape["type"] == "Octagon":
                    self.draw_octagon(*shape["coords"], self.color, fill_color, save=False)
            self.status_label.config(text="Status: Canvas loaded")

    def toggle_mode(self):
        if self.mode.get() == "Draw":
            self.remove_control_points()
            self.mode.set("Delete")
        elif self.mode.get() == "Delete":
            self.remove_control_points()
            self.mode.set("Rotate")
        elif self.mode.get() == "Rotate":
            self.remove_control_points()
            self.mode.set("Resize")
        else:
            self.remove_control_points()
            self.mode.set("Draw")
        self.status_label.config(text=f"Status: {self.mode.get()} mode")

    def on_canvas_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.mode.get() == "Draw":
            if self.selected_shape.get() == "Point":
                self.draw_point(event.x, event.y, self.color, self.color)
            else:
                self.current_shape_id = self.get_shape_at_coords(event.x, event.y)
                if self.current_shape_id:
                    self.moving_shape = True
                else:
                    self.current_shape_id = None
                    self.moving_shape = False
        elif self.mode.get() == "Delete":
            shape_id = self.get_shape_at_coords(event.x, event.y)
            if shape_id:
                self.canvas.delete(shape_id)
                self.shapes = [shape for shape in self.shapes if shape["id"] != shape_id]
                self.status_label.config(text="Status: Shape deleted")
        elif self.mode.get() == "Rotate":
            shape_id = self.get_shape_at_coords(event.x, event.y)
            if shape_id:
                self.rotating_shape = True
                self.current_shape_id = shape_id
                self.canvas.itemconfig(shape_id, outline="red")
        elif self.mode.get() == "Resize":
            shape_id = self.get_shape_at_coords(event.x, event.y)
            if shape_id:
                self.resizing_shape = True
                self.current_shape_id = shape_id
                self.add_control_points(shape_id)

    def on_canvas_drag(self, event):
        if self.mode.get() == "Draw":
            if self.moving_shape and self.current_shape_id:
                dx = event.x - self.start_x
                dy = event.y - self.start_y
                self.canvas.move(self.current_shape_id, dx, dy)
                self.start_x, self.start_y = event.x, event.y
            else:
                self.canvas.delete("preview")
                if self.selected_shape.get() in ["Line", "Circle", "Square", "Triangle", "Octagon"]:
                    self.draw_shape(event.x, event.y, self.color, self.color, "preview")
        elif self.mode.get() == "Rotate" and self.rotating_shape and self.current_shape_id:
            self.rotate_shape(self.current_shape_id, self.start_x, self.start_y, event.x, event.y)
        elif self.mode.get() == "Resize" and self.resizing_shape and self.current_shape_id:
            self.resize_shape(self.current_shape_id, event.x, event.y)

    def on_canvas_release(self, event):
        if self.mode.get() == "Draw":
            if self.moving_shape:
                self.moving_shape = False
                self.current_shape_id = None
            elif self.selected_shape.get() in ["Line", "Circle", "Square", "Triangle", "Octagon"]:
                self.canvas.delete("preview")
                self.draw_shape(event.x, event.y, self.color, self.color)
        elif self.mode.get() == "Rotate" and self.rotating_shape:
            self.rotating_shape = False
            self.current_shape_id = None
            self.canvas.itemconfig("all", outline="black")
        elif self.mode.get() == "Resize" and self.resizing_shape:
            self.resizing_shape = False
            self.current_shape_id = None
            if not self.get_shape_at_coords(event.x, event.y):
                self.remove_control_points()

    def draw_point(self, x, y, color, fill, save=True):
        point_id = self.canvas.create_oval(x, y, x+1, y+1, fill=fill, outline=color)
        if save:
            self.shapes.append({"type": "Point", "id": point_id})
    
    def draw_line(self, x1, y1, x2, y2, color, fill=None, tag=None, save=True):
        line_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, tags=tag)
        if save:
            self.shapes.append({"type": "Line", "id": line_id})
        
    def draw_circle(self, x1, y1, x2, y2, color, fill, tag=None, save=True):
        r = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        circle_id = self.canvas.create_oval(x1-r, y1-r, x1+r, y1+r, outline=color, fill=fill, tags=tag)
        if save:
            self.shapes.append({"type": "Circle", "id": circle_id})
        
    def draw_square(self, x1, y1, x2, y2, color, fill, tag=None, save=True):
        size = min(abs(x2 - x1), abs(y2 - y1))
        square_id = self.canvas.create_rectangle(x1, y1, x1 + size, y1 + size, outline=color, fill=fill, tags=tag)
        if save:
            self.shapes.append({"type": "Square", "id": square_id})
        
    def draw_triangle(self, x1, y1, x2, y2, color, fill, tag=None, save=True):
        points = [x1, y1, x2, y2, (x1 + x2)/2, y1 - (x2 - x1) * (3**0.5)/2]
        triangle_id = self.canvas.create_polygon(points, outline=color, fill=fill, tags=tag)
        if save:
            self.shapes.append({"type": "Triangle", "id": triangle_id})
        
    def draw_octagon(self, x1, y1, x2, y2, color, fill, tag=None, save=True):
        r = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        points = [(x1 + r * math.cos(math.pi/4 * i), y1 + r * math.sin(math.pi/4 * i)) for i in range(8)]
        octagon_id = self.canvas.create_polygon(points, outline=color, fill=fill, tags=tag)
        if save:
            self.shapes.append({"type": "Octagon", "id": octagon_id})

    def draw_shape(self, x, y, color, fill, tag=None):
        shape = self.selected_shape.get()
        if shape == "Line":
            self.draw_line(self.start_x, self.start_y, x, y, color, tag=tag)
        elif shape == "Circle":
            self.draw_circle(self.start_x, self.start_y, x, y, color, fill, tag=tag)
        elif shape == "Square":
            self.draw_square(self.start_x, self.start_y, x, y, color, fill, tag=tag)
        elif shape == "Triangle":
            self.draw_triangle(self.start_x, self.start_y, x, y, color, fill, tag=tag)
        elif shape == "Octagon":
            self.draw_octagon(self.start_x, self.start_y, x, y, color, fill, tag=tag)

    def get_shape_at_coords(self, x, y):
        overlapping = self.canvas.find_overlapping(x, y, x, y)
        for shape in self.shapes:
            if shape["id"] in overlapping:
                return shape["id"]
        return None

    def rotate_shape(self, shape_id, x1, y1, x2, y2):
        coords = self.canvas.coords(shape_id)
        cx, cy = self.get_shape_center(coords)
        angle = math.atan2(y2 - cy, x2 - cx) - math.atan2(y1 - cy, x1 - cx)
        new_coords = self.rotate_coords(coords, cx, cy, angle)
        self.canvas.coords(shape_id, *new_coords)

    def resize_shape(self, shape_id, x, y):
        coords = self.canvas.coords(shape_id)
        cx, cy = self.get_shape_center(coords)
        
        start_dist = ((self.start_x - cx)**2 + (self.start_y - cy)**2)**0.5
        
        current_dist = ((x - cx)**2 + (y - cy)**2)**0.5
        
        resize_factor = 0.01
        
        scale_factor = current_dist / start_dist
        
        scale_factor = (1 + (scale_factor - 1) * resize_factor)
        
        new_coords = self.scale_coords_smooth(coords, cx, cy, scale_factor)
        
        self.canvas.coords(shape_id, *new_coords)
        
        self.update_control_points(shape_id)


    def scale_coords_smooth(self, coords, cx, cy, scale):
        new_coords = []
        for i in range(0, len(coords), 2):
            x, y = coords[i], coords[i+1]
            x = cx + (x - cx) * scale
            y = cy + (y - cy) * scale
            new_coords.extend([x, y])
        return new_coords

    
    
    def rotate_coords(self, coords, cx, cy, angle):
        new_coords = []
        for i in range(0, len(coords), 2):
            x, y = coords[i], coords[i+1]
            x -= cx
            y -= cy
            x_new = x * math.cos(angle) - y * math.sin(angle)
            y_new = x * math.sin(angle) + y * math.cos(angle)
            new_coords.extend([x_new + cx, y_new + cy])
        return new_coords

    def get_shape_center(self, coords):
        x_coords = coords[0::2]
        y_coords = coords[1::2]
        return sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)

    def add_control_points(self, shape_id):
        self.remove_control_points()
        coords = self.canvas.coords(shape_id)
        for i in range(0, len(coords), 2):
            x, y = coords[i], coords[i+1]
            control_point_id = self.canvas.create_rectangle(x-5, y-5, x+5, y+5, outline="blue", fill="blue")
            self.control_point_ids.append(control_point_id)

    def update_control_points(self, shape_id):
        self.remove_control_points()
        self.add_control_points(shape_id)

    def remove_control_points(self):
        for cp_id in self.control_point_ids:
            self.canvas.delete(cp_id)
        self.control_point_ids.clear()


if __name__ == "__main__":
    app = ShapeDrawer()
    app.mainloop()
