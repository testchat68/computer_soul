#!/usr/bin/env python3
"""
Душата на компютъра + CPU/Memory графики + Времето в Сандански + хардуерни температури + часовник
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


class SoulMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Душата на компютъра")
        self.geometry("340x740")
        self.minsize(300, 600)
        self.configure(bg="#1a1a1a")
        self.attributes("-topmost", True)
        self.topmost = True

        # История
        self.history_len = 60
        self.num_threads = self._get_num_threads()
        self.cpu_histories = [deque([0.0] * self.history_len, maxlen=self.history_len) for _ in range(self.num_threads)]
        self.mem_history = deque([0.0] * self.history_len, maxlen=self.history_len)
        self.prev_idles = [0] * self.num_threads
        self.prev_totals = [0] * self.num_threads
        self._init_cpu()
        self.mem_total_kb = self._get_mem_total()

        # Цветове
        self.bg = "#1a1a1a"
        self.fg = "#e0e0e0"
        self.cpu_colors = ["#00e5ff", "#ff6d00", "#f50057", "#ffea00"]
        self.mem_color = "#7fff00"
        self.grid_color = "#333333"
        self.label_bg = "#252525"

        # Цветове за времето
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

        # === ГОРНА ЧАСТ ===
        self.title_label = tk.Label(
            self, text="ДУШАТА НА КОМПЮТЪРА",
            font=("DejaVu Sans", 11, "bold"),
            bg=self.bg, fg="#cccccc"
        )
        self.title_label.pack(pady=(6, 1))

        self.art_label = tk.Label(
            self, text="(•‿•)\n/|\\ /|\\",
            font=("DejaVu Sans Mono", 15),
            bg=self.bg, fg=self.soul_colors["calm"],
            justify="center"
        )
        self.art_label.pack(pady=(1, 2))

        self.top_frame = tk.Frame(self, bg=self.bg)
        self.top_frame.pack(fill=tk.X, padx=8, pady=(0, 1))

        self.cpu_label = tk.Label(
            self.top_frame, text="CPU: --%",
            font=("DejaVu Sans", 10, "bold"),
            fg=self.cpu_colors[0], bg=self.label_bg,
            padx=5, pady=2
        )
        self.cpu_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self.mem_label = tk.Label(
            self.top_frame, text="MEM: --/-- GB",
            font=("DejaVu Sans", 10, "bold"),
            fg=self.mem_color, bg=self.label_bg,
            padx=5, pady=2
        )
        self.mem_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        self.temp_label = tk.Label(
            self, text="Темп: --",
            font=("DejaVu Sans", 8),
            bg=self.bg, fg="#aaaaaa"
        )
        self.temp_label.pack(pady=(1, 1))

        self.poem_label = tk.Label(
            self, text="",
            font=("DejaVu Sans", 9),
            bg=self.bg, fg="#dddddd",
            wraplength=310, justify="center"
        )
        self.poem_label.pack(pady=(3, 2))

        self.btn_frame = tk.Frame(self, bg=self.bg)
        self.btn_frame.pack(fill=tk.X, padx=8, pady=(0, 3))

        self.topmost_btn = tk.Button(
            self.btn_frame,
            text="Always on Top: ON",
            font=("DejaVu Sans", 8),
            bg="#333333",
            fg="#e0e0e0",
            activebackground="#444444",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=6, pady=1,
            command=self._toggle_topmost
        )
        self.topmost_btn.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0, height=145)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 2))
        self.canvas.bind("<Configure>", self._on_resize)

        # === ПРОГНОЗА ===
        self.weather_text = tk.Text(
            self,
            height=9,
            font=("DejaVu Sans", 11),
            bg=self.bg,
            fg="#e0e0e0",
            bd=0,
            highlightthickness=0,
            wrap="none",
            state="disabled"
        )
        self.weather_text.pack(fill=tk.X, padx=10, pady=(2, 2))

        self.weather_text.tag_configure("center", justify="center")
        self.weather_text.tag_configure("header", foreground="#cccccc")
        self.weather_text.tag_configure("day", foreground=self.color_day, font=("DejaVu Sans", 11, "bold"))
        self.weather_text.tag_configure("max", foreground=self.color_max)
        self.weather_text.tag_configure("min", foreground=self.color_min)
        self.weather_text.tag_configure("desc", foreground=self.color_desc)

        # freemeteo.bg линк
        self.freemeteo_label = tk.Label(
            self,
            text="freemeteo.bg",
            font=("DejaVu Sans", 9, "underline"),
            bg=self.bg,
            fg="#00e5ff",
            cursor="hand2"
        )
        self.freemeteo_label.pack(pady=(0, 4))
        self.freemeteo_label.bind(
            "<Button-1>",
            lambda e: webbrowser.open(
                "https://freemeteo.bg/weather/sandanski/hourly-forecast/today/?gid=727447&language=bulgarian&country=bulgaria"
            )
        )

        # === ЧАСОВНИК + ДАТА ===
        self.clock_frame = tk.Frame(self, bg="#222222", highlightbackground="#333333", highlightthickness=1)
        self.clock_frame.pack(fill=tk.X, padx=10, pady=(2, 8))

        self.time_label = tk.Label(
            self.clock_frame,
            text="00:00:00",
            font=("DejaVu Sans Mono", 28, "bold"),
            bg="#222222",
            fg="#f50057",          # магента
            pady=8
        )
        self.time_label.pack(fill=tk.X)

        self.date_label = tk.Label(
            self.clock_frame,
            text="01.JAN.2026",
            font=("DejaVu Sans", 11, "bold"),
            bg="#222222",
            fg="#00e5ff",          # синьо
            pady=4
        )
        self.date_label.pack(fill=tk.X)

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
        state = "ON" if self.topmost else "OFF"
        self.topmost_btn.config(text=f"Always on Top: {state}")

    def _on_resize(self, event=None):
        self._draw_graphs()

    def _draw_graphs(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return
        pad = 3
        mid = h // 2
        graph_h = mid - pad * 2
        self._draw_multi_graph(c, 0, pad, w, graph_h, self.cpu_histories, self.cpu_colors, "CPU")
        self._draw_single_graph(c, 0, mid + pad, w, graph_h, self.mem_history, self.mem_color, "MEM")

    def _draw_single_graph(self, canvas, x0, y0, width, height, data, color, label):
        if height < 5 or width < 10:
            return
        canvas.create_rectangle(x0, y0, x0 + width, y0 + height, fill="#222222", outline="#333333", width=1)
        for pct in (0, 50, 100):
            y = y0 + height - (pct / 100.0) * height
            canvas.create_line(x0, y, x0 + width, y, fill=self.grid_color, dash=(2, 3))
        n = len(data)
        if n < 2:
            return
        points = []
        for i, val in enumerate(data):
            x = x0 + (i / (n - 1)) * (width - 1)
            y = y0 + height - (val / 100.0) * height
            points.extend([x, y])
        if len(points) >= 4:
            canvas.create_line(*points, fill=color, width=1.5)
        if height > 18:
            canvas.create_text(x0 + 5, y0 + 3, text=label, anchor="nw", fill=color, font=("DejaVu Sans", 8, "bold"))

    def _draw_multi_graph(self, canvas, x0, y0, width, height, histories, colors, label):
        if height < 5 or width < 10:
            return
        canvas.create_rectangle(x0, y0, x0 + width, y0 + height, fill="#222222", outline="#333333", width=1)
        for pct in (0, 50, 100):
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

    def _get_state(self, cpu, ram):
        if cpu < 25 and ram < 25:
            return "night"
        load = max(cpu, ram)
        if load < 35:
            return "calm"
        elif load < 65:
            return "medium"
        elif load < 85:
            return "high"
        else:
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
        if code == 0:
            return "SUNNY"
        if code in (1, 2):
            return "PARTLY"
        if code == 3:
            return "CLOUDY"
        if code in (45, 48):
            return "FOGGY"
        if 51 <= code <= 57:
            return "DRIZZLE"
        if code in (61, 63, 65, 66, 67, 80, 81, 82):
            return "RAIN"
        if code in (71, 73, 75, 77, 85, 86):
            return "SNOW"
        if code in (95, 96, 99):
            return "STORM"
        return "CLOUDY"

    def _update_weather(self):
        now = time.time()
        if now - self.last_weather_update < self.weather_interval and self.last_weather_update != 0:
            self.after(60000, self._update_weather)
            return
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast?"
                "latitude=41.5667&longitude=23.2833&"
                "daily=temperature_2m_max,temperature_2m_min,weathercode&"
                "timezone=Europe/Sofia&forecast_days=7&"
                "models=ecmwf_ifs025"
            )
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
                self.weather_text.insert(tk.END, f"{day_name}   ", ("day", "center"))
                self.weather_text.insert(tk.END, f"{tmax[i]:.0f}°", ("max", "center"))
                self.weather_text.insert(tk.END, " / ", ("day", "center"))
                self.weather_text.insert(tk.END, f"{tmin[i]:.0f}°", ("min", "center"))
                self.weather_text.insert(tk.END, f"  {desc}\n", ("desc", "center"))
            self.weather_text.config(state="disabled")
            self.last_weather_update = now
        except Exception:
            self.weather_text.config(state="normal")
            self.weather_text.delete("1.0", tk.END)
            self.weather_text.insert(tk.END, "Сандански • няма връзка", "header")
            self.weather_text.config(state="disabled")
        self.after(60000, self._update_weather)

    def _update(self):
        # Час и дата
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M/%S"))
        self.date_label.config(text=now.strftime("%d.%b.%Y").upper())

        # CPU / MEM / душа
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
        self.mem_label.config(text=f"MEM: {used_gb:.1f}/{total_gb:.1f} GB")
        self.temp_label.config(text=self._get_hardware_temps())
        self._draw_graphs()
        self.after(1000, self._update)


if __name__ == "__main__":
    app = SoulMonitor()
    app.mainloop()
