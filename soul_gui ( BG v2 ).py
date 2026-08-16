#!/usr/bin/env python3
"""
Душата на компютъра
"""
import tkinter as tk
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
        self.minsize(300, 750)
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
        self.grid_color = "#555555"

        self.color_max = "#f50057"
        self.color_min = "#00e5ff"
        self.color_day = "#ff6d00"
        self.color_desc = "#ffea00"

        self.soul_colors = {
            "calm": "#00ff9f",
            "medium": "#ffd700",
            "high": "#ff8c00",
            "critical": "#ff3333",
            "night": "#00e5ff"
        }

        self.arts = {
            "calm": ["(•‿•)\n/|\\ /|\\", "(◠‿◠)\n/|\\ /|\\"],
            "medium": ["(•_•)\n/|\\ /|\\", "(¬_¬)\n/|\\ /|\\"],
            "high": ["(ಠ_ಠ)\n/|\\ /|\\", "(╬ಠ益ಠ)\n/|\\ /|\\"],
            "critical": ["(╯°□°)╯\n/|\\ /|\\", "(ノಠ益ಠ)ノ\n/|\\ /|\\"],
            "night": ["(－_－) zzZ\n/|\\ /|\\", "(￣o￣) zZ\n/|\\ /|\\"]
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

        # === UI ===
        self.title_label = tk.Label(self, text="ДУШАТА НА КОМПЮТЪРА", font=("DejaVu Sans", 11, "bold"),
                                    bg=self.bg, fg="#cccccc")
        self.title_label.pack(pady=(6, 1))

        self.art_label = tk.Label(self, text="(•‿•)\n/|\\ /|\\", font=("DejaVu Sans Mono", 15),
                                  bg=self.bg, fg=self.soul_colors["calm"], justify="center")
        self.art_label.pack(pady=(1, 4))

        self.separator = tk.Frame(self, height=1, bg="#444444")
        self.separator.pack(fill=tk.X, padx=25, pady=(0, 4))

        self.temp_label = tk.Label(self, text="Темп: --", font=("DejaVu Sans", 8),
                                   bg=self.bg, fg="#aaaaaa")
        self.temp_label.pack(pady=(1, 1))

        self.poem_label = tk.Label(self, text="", font=("DejaVu Sans", 9),
                                   bg=self.bg, fg="#dddddd", wraplength=310, justify="center")
        self.poem_label.pack(pady=(3, 2))

        self.btn_frame = tk.Frame(self, bg=self.bg)
        self.btn_frame.pack(fill=tk.X, padx=8, pady=(0, 10))

        self.topmost_btn = tk.Button(self.btn_frame, text="Always on Top: ON", font=("DejaVu Sans", 8),
                                     bg="#333333", fg="#e0e0e0", activebackground="#444444",
                                     activeforeground="#ffffff", relief=tk.FLAT, padx=6, pady=1,
                                     command=self._toggle_topmost)
        self.topmost_btn.pack(side=tk.LEFT)

        self.uptime_label = tk.Label(self.btn_frame, text="UpTime: --", font=("DejaVu Sans", 8),
                                     bg=self.bg, fg="#7fff00")
        self.uptime_label.pack(side=tk.RIGHT)

        self.cpu_label = tk.Label(self, text="CPU: --%", font=("DejaVu Sans", 10, "bold"),
                                  fg=self.cpu_colors[0], bg=self.bg)
        self.cpu_label.pack(pady=(4, 2))

        self.cpu_canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0, height=95)
        self.cpu_canvas.pack(fill=tk.X, padx=6, pady=(0, 12))
        self.cpu_canvas.bind("<Configure>", self._on_resize)

        self.mem_label = tk.Label(self, text="MEM: --/-- GB", font=("DejaVu Sans", 10, "bold"),
                                  fg=self.mem_color, bg=self.bg)
        self.mem_label.pack(pady=(2, 2))

        self.mem_canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0, height=120)
        self.mem_canvas.pack(fill=tk.X, padx=6, pady=(0, 4))
        self.mem_canvas.bind("<Configure>", self._on_resize)

        self.weather_text = tk.Text(self, height=9, font=("DejaVu Sans", 11),
                                    bg=self.bg, fg="#e0e0e0", bd=0, highlightthickness=0,
                                    wrap="none", state="disabled")
        self.weather_text.pack(fill=tk.X, padx=10, pady=(2, 2))

        self.weather_text.tag_configure("center", justify="center")
        self.weather_text.tag_configure("header", foreground="#cccccc")
        self.weather_text.tag_configure("day", foreground=self.color_day, font=("DejaVu Sans", 11, "bold"))
        self.weather_text.tag_configure("max", foreground=self.color_max)
        self.weather_text.tag_configure("min", foreground=self.color_min)
        self.weather_text.tag_configure("desc", foreground=self.color_desc)

        self.freemeteo_label = tk.Label(self, text="freemeteo.bg", font=("DejaVu Sans", 9, "underline"),
                                        bg=self.bg, fg="#00e5ff", cursor="hand2")
        self.freemeteo_label.pack(pady=(0, 4))
        self.freemeteo_label.bind("<Button-1>", lambda e: webbrowser.open(
            "https://freemeteo.bg/weather/sandanski/hourly-forecast/today/?gid=727447&language=bulgarian&country=bulgaria"))

        self.clock_frame = tk.Frame(self, bg="#222222", highlightbackground="#333333", highlightthickness=1)
        self.clock_frame.pack(fill=tk.X, padx=10, pady=(2, 8))

        self.time_label = tk.Label(self.clock_frame, text="00:00:00", font=("DejaVu Sans Mono", 28, "bold"),
                                   bg="#222222", fg="#f50057", pady=8)
        self.time_label.pack(fill=tk.X)

        self.date_label = tk.Label(self.clock_frame, text="01.JAN.2026", font=("DejaVu Sans", 11, "bold"),
                                   bg="#222222", fg="#00e5ff", pady=4)
        self.date_label.pack(fill=tk.X)

        self.storage_title = tk.Label(self, text="STORAGE", font=("DejaVu Sans", 8, "bold"),
                                      bg=self.bg, fg="#e0e0e0")
        self.storage_title.pack(pady=(4, 3))

        self.disks_frame = tk.Frame(self, bg=self.bg)
        self.disks_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.after(300, self._update)
        self.after(1000, self._update_weather)

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
                bar_frame.pack(fill=tk.X, padx=15, pady=(0, 4))
                bar_frame.pack_propagate(False)

                fill = tk.Frame(bar_frame, bg=color)
                fill.place(relx=0, rely=0, relheight=1, relwidth=0)

                self.disk_widgets.append({"lbl1": lbl1, "lbl2": lbl2, "fill": fill})

        for i, disk in enumerate(disks):
            if i >= len(self.disk_widgets):
                break
            w = self.disk_widgets[i]
            w["lbl1"].config(text=f"{disk['name']}: {disk['used']:.1f}/{disk['total']:.1f} GB ({disk['percent']:.0f}%)")
            w["lbl2"].config(text=f"Read: {disk['read']:.1f} MB/s   Write: {disk['write']:.1f} MB/s")
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

    def _draw_graphs(self):
        c = self.cpu_canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w > 10 and h > 10:
            self._draw_multi_graph(c, 0, 2, w, h - 4, self.cpu_histories, self.cpu_colors, "CPU")

        c2 = self.mem_canvas
        c2.delete("all")
        w2, h2 = c2.winfo_width(), c2.winfo_height()
        if w2 > 10 and h2 > 10:
            self._draw_mem_circle(c2, w2, h2)

    def _draw_multi_graph(self, canvas, x0, y0, width, height, histories, colors, label):
        if height < 5 or width < 10:
            return
        canvas.create_rectangle(x0, y0, x0 + width, y0 + height, fill="#222222", outline="#00e5ff", width=1)
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
        if height > 18:
            canvas.create_text(x0 + 5, y0 + 3, text=label, anchor="nw", fill=colors[0], font=("DejaVu Sans", 8, "bold"))

    def _draw_mem_circle(self, canvas, width, height):
        if height < 20:
            return
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2 - 8

        # Фон = свободна памет → зелено
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                           fill="#017301", outline="#017301", width=2)

        mem_pct = self.mem_history[-1] if self.mem_history else 0.0

        # Заетата част → магента
        if mem_pct > 0.5:
            canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius,
                              start=90, extent=-(mem_pct / 100.0) * 360,
                              fill="#8B0000", outline="", style=tk.PIESLICE)
        # Пунктирни кръстосани линии
        canvas.create_line(cx, cy - radius, cx, cy + radius,
                   fill=self.grid_color, dash=(2, 3))          # вертикална
        canvas.create_line(cx - radius, cy, cx + radius, cy,
                   fill=self.grid_color, dash=(2, 3))          # хоризонтална
        # Диагонали (остават вътре в кръга)
        d = radius * 0.7071
        canvas.create_line(cx - d, cy - d, cx + d, cy + d,
                   fill=self.grid_color, dash=(2, 3))
        canvas.create_line(cx - d, cy + d, cx + d, cy - d,
                   fill=self.grid_color, dash=(2, 3)) # /

        # Надписи
        tx = cx + radius * 1.25
        ty = cy - radius * 0.55
        canvas.create_text(tx, ty, text="Used RAM", anchor="w",
                           fill="#f50057", font=("DejaVu Sans", 8, "bold"))
        canvas.create_text(tx, ty + 13, text=f"     {mem_pct:.0f}%", anchor="w",
                           fill="#f50057", font=("DejaVu Sans", 8, "bold"))
        
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
        if code in (1, 2): return "PARTLY"
        if code == 3: return "CLOUDY"
        if code in (45, 48): return "FOGGY"
        if 51 <= code <= 57: return "DRIZZLE"
        if code in (61, 63, 65, 66, 67, 80, 81, 82): return "RAIN"
        if code in (71, 73, 75, 77, 85, 86): return "SNOW"
        if code in (95, 96, 99): return "STORM"
        return "CLOUDY"

    def _update_weather(self):
        now = time.time()
        if now - self.last_weather_update < self.weather_interval and self.last_weather_update != 0:
            self.after(60000, self._update_weather)
            return
        try:
            url = ("https://api.open-meteo.com/v1/forecast?"
                   "latitude=41.5667&longitude=23.2833&"
                   "daily=temperature_2m_max,temperature_2m_min,weathercode&"
                   "timezone=Europe/Sofia&forecast_days=7&models=ecmwf_ifs025")
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            days = data["daily"]["time"]
            tmax = data["daily"]["temperature_2m_max"]
            tmin = data["daily"]["temperature_2m_min"]
            codes = data["daily"]["weathercode"]
            bg_days = ["Пон", "Вто", "Сря", "Чет", "Пет", "Съб", "Нед"]
            self.weather_text.config(state="normal")
            self.weather_text.delete("1.0", tk.END)
            self.weather_text.insert(tk.END, "Сандански • 7 дни\n", ("header", "center"))
            for i in range(7):
                dt = datetime.strptime(days[i], "%Y-%m-%d")
                day_name = bg_days[dt.weekday()]
                desc = self._weather_desc(codes[i])
                self.weather_text.insert(tk.END, f"{day_name} ", ("day", "center"))
                self.weather_text.insert(tk.END, f"{tmax[i]:.0f}°", ("max", "center"))
                self.weather_text.insert(tk.END, " / ", ("day", "center"))
                self.weather_text.insert(tk.END, f"{tmin[i]:.0f}°", ("min", "center"))
                self.weather_text.insert(tk.END, f" {desc}\n", ("desc", "center"))
            self.weather_text.config(state="disabled")
            self.last_weather_update = now
        except Exception:
            self.weather_text.config(state="normal")
            self.weather_text.delete("1.0", tk.END)
            self.weather_text.insert(tk.END, "Сандански • няма връзка", "header")
            self.weather_text.config(state="disabled")
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

        self.art_label.config(text=random.choice(self.arts[state]), fg=color)
        self.title_label.config(fg=color)
        self.poem_label.config(text=f"„{self.last_poem}“", fg=color)
        self.cpu_label.config(text=f"CPU: {avg_cpu:.0f}% ({self.num_threads} thr)")
        self.mem_label.config(text=f"RAM: {used_gb:.1f}/{total_gb:.1f} GB")
        self.temp_label.config(text=self._get_hardware_temps())
        self._draw_graphs()
        self.after(1000, self._update)


if __name__ == "__main__":
    app = SoulMonitor()
    app.mainloop()
