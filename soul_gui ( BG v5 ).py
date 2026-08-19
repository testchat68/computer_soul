#!/usr/bin/env python3
"""
Душата на компютъра
"""
import tkinter as tk
import tkinter.font as tkfont
from collections import deque
import random
import json
import urllib.request
from datetime import datetime
import os
import time
import webbrowser
import shutil

class SoulMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Душата на компютъра")
        self.geometry("340x920")
        self.minsize(300, 740)
        self.configure(bg="#1a1a1a")
        self.attributes("-topmost", True)
        self.topmost = True

        self.history_len = 60
        self.num_threads = self._get_num_threads()
        self.cpu_histories = [deque([0.0] * self.history_len, maxlen=self.history_len) for _ in range(self.num_threads)]
        self.mem_history = deque([0.0] * self.history_len, maxlen=self.history_len)
        self.prev_idles = [0] * self.num_threads
        self.prev_totals = [0] * self.num_threads
        self._init_cpu()
        self.mem_total_kb = self._get_mem_total()
        self.prev_disk_stats = {}
        self.last_disk_time = time.time()
        self.disk_widgets = []

        self.bg = "#1a1a1a"
        self.fg = "#e0e0e0"
        self.cpu_colors = ["#00e5ff", "#ff6d00", "#f50057", "#ffea00"]
        self.mem_color = "#7fff00"
        self.used_ram_color = "#ff8a9a"
        self.clock_color = "#ff8a9a"
        self.grid_color = "#555555"
        self.color_day = "#ffffff"
        self.color_desc = "#ffc44d"
        self.color_temp_cold = "#00e5ff"
        self.color_temp_mild = "#7fff00"
        self.color_temp_hot = "#f50057"
        self.color_temp_freeze = "#ffffff"
        self.color_temp_max = "#ff4d2e"
        self.color_header = "#ffcc80"

        self.wf = self._pick_weather_font()

        self.soul_colors = {
            "calm": "#00ff9f",
            "medium": "#ffd700",
            "high": "#ff8c00",
            "critical": "#ff3333",
            "night": "#00e5ff"
        }

        self.poems = {
            "calm": [
                "Системата диша спокойно...",
                "Тишината е лукс, който си заслужаваме.",
                "Байтовете танцуват бавно и красиво.",
                "Днес светът е лек."
            ],
            "medium": [
                "Нещо се движи под повърхността...",
                "Процесорът започна да мисли по-силно.",
                "RAM-ът държи спомени, които тежат.",
                "Балансът е крехък, но все още го има."
            ],
            "high": [
                "Сърцето ми бие по-бързо.",
                "Твърде много мисли наведнъж...",
                "Системата започва да се поти.",
                "Моля те... малко въздух."
            ],
            "critical": [
                "Всичко се разпада на частици!",
                "Аз... не издържам повече...",
                "Светът стана твърде тежък.",
                "Помощ... или поне един рестарт."
            ],
            "night": [
                "Спя сладко...",
                "Дори електроните почиват.",
                "Тихо... почти нищо не се случва.",
                "Сънувам празни процеси."
            ]
        }

        self.last_poem = ""
        self.poem_counter = 0
        self.current_state = "calm"
        self.last_weather_update = 0
        self.weather_interval = 1800
        self.current_temp = None
        self.current_desc = ""

        self.temp_label = tk.Label(self, text="Темп: --",
                                   font=("DejaVu Sans", 9),
                                   bg=self.bg, fg="#aaaaaa")
        self.temp_label.pack(pady=(10, 2))

        self.poem_label = tk.Label(self, text="",
                                   font=("DejaVu Sans", 9),
                                   bg=self.bg, fg="#dddddd", wraplength=300, justify="center")
        self.poem_label.pack(pady=(2, 8))

        self.btn_frame = tk.Frame(self, bg=self.bg)
        self.btn_frame.pack(fill=tk.X, padx=14, pady=(0, 10))

        self.topmost_btn = tk.Button(self.btn_frame, text="Always on Top: ON",
                                     font=("DejaVu Sans", 8),
                                     bg="#333333", fg="#e0e0e0",
                                     activebackground="#444444", activeforeground="#ffffff",
                                     relief=tk.FLAT, padx=8, pady=2,
                                     command=self._toggle_topmost)
        self.topmost_btn.pack(side=tk.LEFT)

        self.uptime_label = tk.Label(self.btn_frame, text="UpTime: --",
                                     font=("DejaVu Sans", 8),
                                     bg=self.bg, fg="#7fff00")
        self.uptime_label.pack(side=tk.RIGHT)

        self.cpu_box = tk.Frame(self, bg=self.bg,
                                highlightbackground="#00e5ff",
                                highlightthickness=2,
                                highlightcolor="#00e5ff")
        self.cpu_box.pack(fill=tk.X, padx=12, pady=(2, 8))

        self.cpu_label = tk.Label(self.cpu_box, text="CPU: --%",
                                  font=("DejaVu Sans", 14, "bold"),
                                  fg=self.cpu_colors[0], bg=self.bg)
        self.cpu_label.pack(pady=(8, 4))

        self.cpu_canvas = tk.Canvas(self.cpu_box, bg=self.bg, highlightthickness=0, height=95)
        self.cpu_canvas.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.cpu_canvas.bind("<Configure>", self._on_resize)

        self.mem_box = tk.Frame(self, bg=self.bg,
                                highlightbackground="#7fff00",
                                highlightthickness=2,
                                highlightcolor="#7fff00")
        self.mem_box.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.mem_label = tk.Label(self.mem_box, text="RAM: --/-- GB",
                                  font=("DejaVu Sans", 14, "bold"),
                                  fg=self.mem_color, bg=self.bg)
        self.mem_label.pack(pady=(8, 4))

        self.mem_canvas = tk.Canvas(self.mem_box, bg=self.bg, highlightthickness=0, height=120)
        self.mem_canvas.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.mem_canvas.bind("<Configure>", self._on_resize)

        self.weather_box = tk.Frame(self, bg=self.bg,
                                    highlightbackground="#ff6d00",
                                    highlightthickness=2,
                                    highlightcolor="#ff6d00")
        self.weather_box.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.weather_content = tk.Frame(self.weather_box, bg=self.bg)
        self.weather_content.pack(fill=tk.X, padx=8, pady=(8, 6))

        self.weather_header = tk.Label(
            self.weather_content,
            text="Сандански • сега",
            font=(self.wf, 12, "bold"),
            bg=self.bg, fg=self.color_header
        )
        self.weather_header.pack(anchor="w", pady=(0, 6))

        now_row = tk.Frame(self.weather_content, bg=self.bg)
        now_row.pack(fill=tk.X, pady=(0, 10))

        now_info = tk.Frame(now_row, bg=self.bg)
        now_info.pack(side=tk.RIGHT, padx=(8, 2))

        self.now_temp_label = tk.Label(now_info, text="--°",
                                       font=(self.wf, 32),
                                       bg=self.bg, fg=self.color_temp_hot)
        self.now_temp_label.pack(anchor="e")

        self.now_desc_label = tk.Label(now_info, text="--",
                                       font=(self.wf, 12),
                                       bg=self.bg, fg=self.color_desc)
        self.now_desc_label.pack(anchor="e")

        self.scale_canvas = tk.Canvas(now_row, bg=self.bg, highlightthickness=0, height=58)
        self.scale_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.scale_canvas.bind("<Configure>", lambda e: self._draw_temp_scale())

        self.forecast_frame = tk.Frame(self.weather_content, bg=self.bg)
        self.forecast_frame.pack(fill=tk.X)
        self.forecast_frame.columnconfigure(0, minsize=52)
        self.forecast_frame.columnconfigure(1, minsize=44)
        self.forecast_frame.columnconfigure(2, minsize=44)
        self.forecast_frame.columnconfigure(3, weight=1)

        self.day_labels = []
        self.max_labels = []
        self.min_labels = []
        self.desc_labels = []

        for i in range(7):
            r = i * 2
            if i > 0:
                sep = tk.Frame(self.forecast_frame, bg="#333333", height=1)
                sep.grid(row=r - 1, column=0, columnspan=4, sticky="ew", pady=(3, 3))

            day_lbl = tk.Label(self.forecast_frame, text="", font=(self.wf, 11),
                               bg=self.bg, fg="#ffffff", anchor="w")
            day_lbl.grid(row=r, column=0, sticky="w", padx=(28, 8), pady=1)

            max_lbl = tk.Label(self.forecast_frame, text="", font=(self.wf, 11),
                               bg=self.bg, fg=self.color_temp_max, anchor="e")
            max_lbl.grid(row=r, column=1, sticky="e", padx=(28, 6), pady=1)

            min_lbl = tk.Label(self.forecast_frame, text="", font=(self.wf, 11),
                               bg=self.bg, fg=self.color_temp_cold, anchor="e")
            min_lbl.grid(row=r, column=2, sticky="e", padx=(10, 10), pady=1)

            desc_lbl = tk.Label(self.forecast_frame, text="", font=(self.wf, 8),
                                bg=self.bg, fg="#9a9a9a", anchor="w")
            desc_lbl.grid(row=r, column=3, sticky="w", padx=(10, 2), pady=1)

            self.day_labels.append(day_lbl)
            self.max_labels.append(max_lbl)
            self.min_labels.append(min_lbl)
            self.desc_labels.append(desc_lbl)

        self.freemeteo_label = tk.Label(
            self.weather_content,
            text="freemeteo.bg",
            font=(self.wf, 9, "underline"),
            bg=self.bg, fg="#00e5ff", cursor="hand2"
        )
        self.freemeteo_label.pack(pady=(10, 2))
        self.freemeteo_label.bind("<Button-1>", lambda e: webbrowser.open(
            "https://freemeteo.bg/weather/sandanski/hourly-forecast/today/?gid=727447&language=bulgarian&country=bulgaria"))

        self.clock_frame = tk.Frame(self, bg="#222222",
                                    highlightbackground="#444444", highlightthickness=1)
        self.clock_frame.pack(fill=tk.X, padx=12, pady=(2, 10))

        self.time_label = tk.Label(self.clock_frame, text="00:00:00",
                                   font=("DejaVu Sans Mono", 28, "bold"),
                                   bg="#222222", fg=self.clock_color, pady=6)
        self.time_label.pack(fill=tk.X)

        self.date_label = tk.Label(self.clock_frame, text="01.JAN.2026",
                                   font=("DejaVu Sans", 11, "bold"),
                                   bg="#222222", fg="#00e5ff", pady=3)
        self.date_label.pack(fill=tk.X)

        #self.storage_title = tk.Label(self, text="STORAGE",
                                      #font=("DejaVu Sans", 9, "bold"),
                                      #bg=self.bg, fg="#e0e0e0")
        #self.storage_title.pack(pady=(6, 4))

        self.disks_frame = tk.Frame(self, bg=self.bg)
        self.disks_frame.pack(fill=tk.X, padx=14, pady=(0, 10))

        self.after(300, self._update)
        self.after(1000, self._update_weather)

    def _pick_weather_font(self):
        available = {name.lower(): name for name in tkfont.families()}
        for name in ("Inter", "Inter Display", "Inter Regular", "Noto Sans", "Manrope", "Montserrat"):
            if name.lower() in available:
                return available[name.lower()]
        return "DejaVu Sans"

    def _temp_color(self, t):
        if t < 5:
            return self.color_temp_freeze
        if t <= 20:
            return self.color_temp_cold
        if t <= 26:
            return self.color_temp_mild
        return self.color_temp_hot

    def _temp_to_x(self, t, x0, width):
        t = max(-30.0, min(50.0, float(t)))
        return x0 + ((t + 30.0) / 80.0) * width

    def _draw_temp_scale(self):
        c = self.scale_canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 40 or h < 30:
            return

        x0, x1 = 10, w - 10
        bar_w = max(1, x1 - x0)
        y = 20
        bh = 14

        stops = [
            (0.00, (0, 80, 210)),
            (0.375, (0, 229, 255)),
            (0.625, (80, 220, 40)),
            (0.75, (255, 220, 0)),
            (0.88, (255, 90, 30)),
            (1.00, (245, 0, 87)),
        ]

        def lerp(a, b, t):
            return int(a + (b - a) * t)

        def color_at(t):
            for s in range(len(stops) - 1):
                t0, c0 = stops[s]
                t1, c1 = stops[s + 1]
                if t0 <= t <= t1:
                    u = (t - t0) / (t1 - t0) if t1 > t0 else 0
                    return f"#{lerp(c0[0], c1[0], u):02x}{lerp(c0[1], c1[1], u):02x}{lerp(c0[2], c1[2], u):02x}"
            return "#f50057"

        steps = max(60, int(bar_w))
        for i in range(steps):
            t = i / max(1, steps - 1)
            x = x0 + t * bar_w
            c.create_line(x, y, x, y + bh, fill=color_at(t))

        c.create_oval(x0 - 1, y, x0 + bh - 1, y + bh, fill=color_at(0.0), outline="")
        c.create_oval(x1 - bh + 1, y, x1 + 1, y + bh, fill=color_at(1.0), outline="")

        for val, txt in ((-30, "-30"), (0, "0"), (20, "20"), (30, "30"), (50, "50")):
            xx = self._temp_to_x(val, x0, bar_w)
            c.create_text(xx, y + bh + 11, text=txt, fill="#888888",
                          font=(self.wf, 7))

        if self.current_temp is not None:
            px = self._temp_to_x(self.current_temp, x0, bar_w)
            c.create_polygon(
                px, y - 3,
                px - 7, y - 14,
                px + 7, y - 14,
                fill=self._temp_color(self.current_temp), outline=""
            )

    def _get_num_threads(self):
        count = 0
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("processor"):
                        count += 1
        except Exception:
            count = 1
        return max(1, count)

    def _get_mem_total(self):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        return int(line.split()[1])
        except Exception:
            return 16 * 1024 * 1024
        return 16 * 1024 * 1024

    def _get_uptime(self):
        try:
            with open("/proc/uptime", "r") as f:
                seconds = float(f.read().split()[0])
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            minutes = int((seconds % 3600) // 60)
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        except Exception:
            return "--"

    def _get_disk_io(self):
        now = time.time()
        delta_t = max(0.1, now - self.last_disk_time)
        current = {}
        try:
            with open("/proc/diskstats", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 14:
                        continue
                    dev = parts[2]
                    if dev[-1].isdigit() and not dev.startswith("nvme"):
                        continue
                    current[dev] = (int(parts[5]), int(parts[9]))
        except Exception:
            return {}
        speeds = {}
        for dev, (r, w) in current.items():
            if dev in self.prev_disk_stats:
                prev_r, prev_w = self.prev_disk_stats[dev]
                read_mb = ((r - prev_r) * 512) / (1024 * 1024) / delta_t
                write_mb = ((w - prev_w) * 512) / (1024 * 1024) / delta_t
                speeds[dev] = (max(0.0, read_mb), max(0.0, write_mb))
            else:
                speeds[dev] = (0.0, 0.0)
        self.prev_disk_stats = current
        self.last_disk_time = now
        return speeds

    def _get_disks(self):
        result = []
        seen = set()
        skip_fs = {"tmpfs", "devtmpfs", "proc", "sysfs", "cgroup", "cgroup2", "pstore", "bpf",
                   "debugfs", "tracefs", "securityfs", "hugetlbfs", "mqueue", "fusectl",
                   "configfs", "devpts", "overlay", "nsfs", "rpc_pipefs", "efivarfs"}
        io_speeds = self._get_disk_io()
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    device = parts[0]
                    mountpoint = parts[1].replace("\\040", " ")
                    fstype = parts[2]
                    if fstype in skip_fs:
                        continue
                    if not (mountpoint == "/" or mountpoint.startswith(("/media/", "/mnt/", "/run/media/"))):
                        continue
                    try:
                        usage = shutil.disk_usage(mountpoint)
                        if usage.total < 512 * 1024 * 1024:
                            continue
                        key = (device, usage.total)
                        if key in seen:
                            continue
                        seen.add(key)
                        total_gb = usage.total / (1024 ** 3)
                        used_gb = usage.used / (1024 ** 3)
                        pct = (usage.used / usage.total) * 100 if usage.total else 0
                        name = "root" if mountpoint == "/" else (os.path.basename(mountpoint) or "USB")
                        base = os.path.basename(device)
                        while base and base[-1].isdigit():
                            base = base[:-1]
                        if base.endswith("p"):
                            base = base[:-1]
                        read_s, write_s = io_speeds.get(base, (0.0, 0.0))
                        result.append({
                            "name": name,
                            "used": used_gb,
                            "total": total_gb,
                            "percent": pct,
                            "read": read_s,
                            "write": write_s
                        })
                    except Exception:
                        continue
        except Exception:
            pass
        return result

    def _update_storage_ui(self, disks):
        if len(self.disk_widgets) != len(disks):
            for w in self.disks_frame.winfo_children():
                w.destroy()
            self.disk_widgets = []
            colors = ["#00e5ff", "#ff6d00", "#f50057", "#ffea00", "#7fff00", "#b388ff"]
            for i, disk in enumerate(disks):
                color = colors[i % len(colors)]
                lbl1 = tk.Label(self.disks_frame, text="", font=("DejaVu Sans", 8),
                                bg=self.bg, fg=color, anchor="center")
                lbl1.pack(fill=tk.X, pady=(6, 0))
                lbl2 = tk.Label(self.disks_frame, text="", font=("DejaVu Sans", 7),
                                bg=self.bg, fg="#aaaaaa", anchor="center")
                lbl2.pack(fill=tk.X, pady=(1, 2))
                bar_frame = tk.Frame(self.disks_frame, bg="#333333", height=9)
                bar_frame.pack(fill=tk.X, padx=18, pady=(0, 6))
                bar_frame.pack_propagate(False)
                fill = tk.Frame(bar_frame, bg=color)
                fill.place(relx=0, rely=0, relheight=1, relwidth=0)
                self.disk_widgets.append({"lbl1": lbl1, "lbl2": lbl2, "fill": fill})

        for i, disk in enumerate(disks):
            if i >= len(self.disk_widgets):
                break
            w = self.disk_widgets[i]
            w["lbl1"].config(text=f"{disk['name']}: {disk['used']:.1f}/{disk['total']:.1f} GB ({disk['percent']:.0f}%)")
            w["lbl2"].config(text=f"Read: {disk['read']:.1f} MB/s  Write: {disk['write']:.1f} MB/s")
            w["fill"].place(relx=0, rely=0, relheight=1, relwidth=min(1.0, disk['percent'] / 100.0))

    def _init_cpu(self):
        data = self._read_all_cpus()
        for i, (idle, total) in enumerate(data):
            if i < self.num_threads:
                self.prev_idles[i] = idle
                self.prev_totals[i] = total

    def _read_all_cpus(self):
        result = []
        try:
            with open("/proc/stat", "r") as f:
                for line in f:
                    if line.startswith("cpu") and not line.startswith("cpu "):
                        parts = line.split()
                        values = [int(x) for x in parts[1:9]]
                        idle = values[3] + values[4]
                        total = sum(values)
                        result.append((idle, total))
        except Exception:
            pass
        while len(result) < self.num_threads:
            result.append((0, 0))
        return result[:self.num_threads]

    def _get_cpu_percents(self):
        data = self._read_all_cpus()
        percents = []
        for i, (idle, total) in enumerate(data):
            idle_delta = idle - self.prev_idles[i]
            total_delta = total - self.prev_totals[i]
            self.prev_idles[i] = idle
            self.prev_totals[i] = total
            if total_delta <= 0:
                percents.append(0.0)
            else:
                usage = 100.0 * (1.0 - idle_delta / total_delta)
                percents.append(max(0.0, min(100.0, usage)))
        return percents

    def _get_mem_info(self):
        mem_available = 0
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        mem_available = int(line.split()[1])
                        break
        except Exception:
            pass
        used_kb = self.mem_total_kb - mem_available
        used_gb = used_kb / (1024 * 1024)
        total_gb = self.mem_total_kb / (1024 * 1024)
        percent = 100.0 * used_kb / self.mem_total_kb if self.mem_total_kb else 0.0
        return percent, used_gb, total_gb

    def _toggle_topmost(self):
        self.topmost = not self.topmost
        self.attributes("-topmost", self.topmost)
        self.topmost_btn.config(text=f"Always on Top: {'ON' if self.topmost else 'OFF'}")

    def _on_resize(self, event=None):
        self._draw_graphs()
        self._draw_temp_scale()

    def _draw_graphs(self):
        c = self.cpu_canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w > 10 and h > 10:
            self._draw_multi_graph(c, 0, 2, w, h - 4, self.cpu_histories, self.cpu_colors)

        c2 = self.mem_canvas
        c2.delete("all")
        w2, h2 = c2.winfo_width(), c2.winfo_height()
        if w2 > 10 and h2 > 10:
            self._draw_mem_circle(c2, w2, h2)

    def _draw_multi_graph(self, canvas, x0, y0, width, height, histories, colors):
        if height < 5 or width < 10:
            return
        canvas.create_rectangle(x0, y0, x0 + width, y0 + height,
                                fill="#222222", outline="#00e5ff", width=1)
        for pct in (0, 25, 50, 75, 100):
            y = y0 + height - (pct / 100.0) * height
            canvas.create_line(x0, y, x0 + width, y, fill=self.grid_color, dash=(2, 3))
        for hist, color in zip(histories, colors):
            n = len(hist)
            if n < 2:
                continue
            points = []
            for i, val in enumerate(hist):
                x = x0 + (i / (n - 1)) * (width - 1)
                y = y0 + height - (val / 100.0) * height
                points.extend([x, y])
            if len(points) >= 4:
                canvas.create_line(*points, fill=color, width=1.3)

    def _draw_mem_circle(self, canvas, width, height):
        if height < 20:
            return
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2 - 8
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                           fill="#7CFFCB", outline="#017301", width=2)
        mem_pct = self.mem_history[-1] if self.mem_history else 0.0
        if mem_pct > 0.5:
            canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius,
                              start=90, extent=-(mem_pct / 100.0) * 360,
                              fill=self.used_ram_color, outline="", style=tk.PIESLICE)
        canvas.create_line(cx, cy - radius, cx, cy + radius, fill=self.grid_color, dash=(2, 3))
        canvas.create_line(cx - radius, cy, cx + radius, cy, fill=self.grid_color, dash=(2, 3))
        d = radius * 0.7071
        canvas.create_line(cx - d, cy - d, cx + d, cy + d, fill=self.grid_color, dash=(2, 3))
        canvas.create_line(cx - d, cy + d, cx + d, cy - d, fill=self.grid_color, dash=(2, 3))
        tx = cx + radius * 1.25
        ty = cy - radius * 0.55
        canvas.create_text(tx, ty, text="Used RAM", anchor="w",
                           fill=self.used_ram_color, font=("DejaVu Sans", 8, "bold"))
        canvas.create_text(tx, ty + 13, text=f" {mem_pct:.0f}%", anchor="w",
                           fill=self.used_ram_color, font=("DejaVu Sans", 8, "bold"))

    def _get_state(self, cpu, ram):
        if cpu < 25 and ram < 25:
            return "night"
        load = max(cpu, ram)
        if load < 35:
            return "calm"
        if load < 65:
            return "medium"
        if load < 85:
            return "high"
        return "critical"

    def _get_hardware_temps(self):
        temps = []
        try:
            for zone in sorted(os.listdir("/sys/class/thermal/")):
                if not zone.startswith("thermal_zone"):
                    continue
                try:
                    with open(f"/sys/class/thermal/{zone}/temp") as f:
                        t = int(f.read().strip()) / 1000.0
                    with open(f"/sys/class/thermal/{zone}/type") as f:
                        typ = f.read().strip().lower()
                    if "tskn" in typ:
                        temps.append(f"tskn {t:.0f}°")
                    elif "pkg" in typ or "cpu" in typ or "x86" in typ:
                        temps.append(f"CPU {t:.0f}°")
                except Exception:
                    continue
        except Exception:
            pass
        return " | ".join(temps) if temps else "Темп: няма данни"

    def _weather_desc(self, code):
        code = int(code)
        if code == 0: return "SUNNY"
        if code == 1: return "MOSTLY SUNNY"
        if code == 2: return "PARTLY CLOUDY"
        if code == 3: return "CLOUDY"
        if code in (45, 48): return "FOGGY"
        if code == 51: return "LIGHT DRIZZLE"
        if code == 53: return "DRIZZLE"
        if code == 55: return "HEAVY DRIZZLE"
        if code in (56, 57): return "FREEZING DRIZZLE"
        if code == 61: return "LIGHT RAIN"
        if code == 63: return "RAIN"
        if code == 65: return "HEAVY RAIN"
        if code in (66, 67): return "FREEZING RAIN"
        if code == 71: return "LIGHT SNOW"
        if code == 73: return "SNOW"
        if code == 75: return "HEAVY SNOW"
        if code == 77: return "SNOW GRAINS"
        if code == 80: return "LIGHT SHOWERS"
        if code == 81: return "SHOWERS"
        if code == 82: return "HEAVY SHOWERS"
        if code == 85: return "LIGHT SNOW"
        if code == 86: return "HEAVY SNOW"
        if code == 95: return "STORM"
        if code in (96, 99): return "HAIL STORM"
        return "CLOUDY"

    def _update_weather(self):
        now = time.time()
        if now - self.last_weather_update < self.weather_interval and self.last_weather_update != 0:
            self.after(60000, self._update_weather)
            return
        try:
            url = ("https://api.open-meteo.com/v1/forecast?"
                   "latitude=41.5667&longitude=23.2833&"
                   "current=temperature_2m,weather_code&"
                   "daily=temperature_2m_max,temperature_2m_min,weathercode&"
                   "timezone=Europe/Sofia&forecast_days=7&models=ecmwf_ifs025")
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = json.loads(resp.read().decode())

            cur = data.get("current", {})
            self.current_temp = float(cur.get("temperature_2m", 0))
            self.current_desc = self._weather_desc(cur.get("weather_code", 0))
            self.now_temp_label.config(text=f"{self.current_temp:.0f}°",
                                       fg=self._temp_color(self.current_temp))
            self.now_desc_label.config(text=self.current_desc)
            self._draw_temp_scale()

            days = data["daily"]["time"]
            tmax = data["daily"]["temperature_2m_max"]
            tmin = data["daily"]["temperature_2m_min"]
            codes = data["daily"]["weathercode"]
            bg_days = ["Пон", "Втор", "Сря", "Четв", "Пет", "Съб", "Нед"]

            self.weather_header.config(text="Сандански • сега", fg=self.color_header)

            for i in range(7):
                dt = datetime.strptime(days[i], "%Y-%m-%d")
                day_name = bg_days[dt.weekday()]
                desc = self._weather_desc(codes[i])
                self.day_labels[i].config(text=day_name, fg="#ffffff")
                self.max_labels[i].config(text=f"{tmax[i]:.0f}°", fg=self.color_temp_max)
                self.min_labels[i].config(text=f"{tmin[i]:.0f}°", fg=self._temp_color(tmin[i]))
                self.desc_labels[i].config(text=desc)

            self.last_weather_update = now
        except Exception:
            self.weather_header.config(text="Сандански • няма връзка", fg="#ff6d00")
            self.now_temp_label.config(text="--°")
            self.now_desc_label.config(text="--")
            self.current_temp = None
            self._draw_temp_scale()
            for i in range(7):
                self.day_labels[i].config(text="")
                self.max_labels[i].config(text="")
                self.min_labels[i].config(text="")
                self.desc_labels[i].config(text="")

        self.after(60000, self._update_weather)

    def _update(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M/%S"))
        self.date_label.config(text=now.strftime("%d.%b.%Y").upper())
        self.uptime_label.config(text=f"UpTime: {self._get_uptime()}")

        disks = self._get_disks()
        self._update_storage_ui(disks)

        cpu_percents = self._get_cpu_percents()
        for i, p in enumerate(cpu_percents):
            self.cpu_histories[i].append(p)
        avg_cpu = sum(cpu_percents) / len(cpu_percents) if cpu_percents else 0.0

        mem_pct, used_gb, total_gb = self._get_mem_info()
        self.mem_history.append(mem_pct)

        state = self._get_state(avg_cpu, mem_pct)
        color = self.soul_colors[state]

        self.poem_counter += 1
        if self.poem_counter >= 7 or not self.last_poem or state != self.current_state:
            self.last_poem = random.choice(self.poems[state])
            self.poem_counter = 0
        self.current_state = state

        self.poem_label.config(text=f"„{self.last_poem}“", fg=color)
        self.cpu_label.config(text=f"CPU: {avg_cpu:.0f}%")
        self.mem_label.config(text=f"RAM: {used_gb:.1f}/{total_gb:.1f} GB")
        self.temp_label.config(text=self._get_hardware_temps())
        self._draw_graphs()
        self.after(1000, self._update)

if __name__ == "__main__":
    app = SoulMonitor()
    app.mainloop()
