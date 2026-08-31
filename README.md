# The Computer's Soul

[![Python](https://img.shields.io/badge/python-3.6+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational?logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![Standard library](https://img.shields.io/badge/deps-stdlib%20only-success)](#requirements)
[![No pip](https://img.shields.io/badge/pip-not%20required-lightgrey)](#how-to-run)
[![Linux](https://img.shields.io/badge/platform-Linux-orange?logo=linux&logoColor=white)](#requirements)
[![/proc](https://img.shields.io/badge/metrics-%2Fproc%20%2B%20%2Fsys-yellow)](#requirements)
[![Always on top](https://img.shields.io/badge/window-always--on--top-blueviolet)](#tips)
[![Desktop](https://img.shields.io/badge/type-desktop%20app-blueviolet)](#how-to-run)
[![.desktop launcher](https://img.shields.io/badge/launcher-.desktop-critical)](#how-to-run)
[![CPU](https://img.shields.io/badge/CPU-per--thread%20graphs-00e5ff)](#the-computers-soul)
[![RAM](https://img.shields.io/badge/RAM-live%20graph-7fff00)](#the-computers-soul)
[![Temps](https://img.shields.io/badge/temps-%2Fsys%2Fclass%2Fthermal-ff6d00)](#the-computers-soul)
[![Disks](https://img.shields.io/badge/storage-usage%20%2B%20R%2FW-ffea00)](#the-computers-soul)
[![Uptime](https://img.shields.io/badge/uptime-%2Fproc%2Fuptime-7fff00)](#the-computers-soul)
[![Weather](https://img.shields.io/badge/weather-Open--Meteo-00e5ff)](https://open-meteo.com/)
[![Forecast](https://img.shields.io/badge/forecast-7%20days-ff6d00)](#the-computers-soul)
[![ECMWF](https://img.shields.io/badge/model-ECMWF%20IFS%200.25°-lightgrey)](https://open-meteo.com/)
[![Cities](https://img.shields.io/badge/cities-Sandanski%20%7C%20Sofia%20%7C%20London-3a7bd5)](#how-to-change-the-city--weather-location)
[![Update](https://img.shields.io/badge/weather%20refresh-30%20min-inactive)](#tips)
[![Clock](https://img.shields.io/badge/clock%20%2B%20date-yes-ff8a9a)](#the-computers-soul)
[![Calendar](https://img.shields.io/badge/calendar-click%20the%20clock-ffcc80)](#tips)
[![Soul moods](https://img.shields.io/badge/soul-5%20moods-00ff9f)](#the-computers-soul)
[![Poems](https://img.shields.io/badge/poems-Bulgarian-yellow)](#the-computers-soul)
[![Dark UI](https://img.shields.io/badge/theme-dark-1a1a1a)](#the-computers-soul)
[![Size](https://img.shields.io/badge/window-340×980-inactive)](#the-computers-soul)
[![Language](https://img.shields.io/badge/UI-Bulgarian-yellow)](#the-computers-soul)
[![Internet](https://img.shields.io/badge/network-only%20for%20weather-lightgrey)](#requirements)
[![Forever Free](https://img.shields.io/badge/license-Forever%20Free-brightgreen)](#license)
[![Use](https://img.shields.io/badge/use-private%20%7C%20public%20%7C%20business-green)](#license)
[![Modify](https://img.shields.io/badge/modify-yes-success)](#license)
[![Contact](https://img.shields.io/badge/contact-good.vibes.github%40gmail.com-red)](#license)

A lightweight, always-on-top system monitor with personality.

Please see the picture:

![The Computer's Soul](Soul.jpg)

It shows:

- Live **CPU** usage (per-thread graphs)
- **Memory** usage graph
- Hardware **temperatures** (where available)
- Disk usage + live read/write speed
- System **uptime**
- A **7-day weather** forecast
- A big **clock + date** (click for calendar)
- Short **poems** that change according to system load (“the soul”)

Built-in cities: **Сандански**, **София**, **Лондон**.  
Weather comes from the free [Open-Meteo](https://open-meteo.com/) API.

---

## Requirements

- Python **3.6+**
- **tkinter** (usually included with Python on Linux)
- **Linux** (uses `/proc` and `/sys` for CPU, memory, temperatures, disks, uptime)

Works best on Linux. On other systems the CPU / memory / temp parts may not work or will show limited data.

No `pip install`. Standard library only. Internet is needed only for the weather panel.

---

## How to run

1. Put the file `soul_gui.py` into your **HOME** folder.
2. Right-click the file → **Options → Permissions** and check all **Execution** boxes.
3. Move `Душата.desktop` onto the **Desktop** and do the same:  
   Right-click → **Options → Permissions** → check all **Execution** boxes.

That's it — now you can use the program.

From a terminal:

```bash
python3 "$HOME/soul_gui.py"
```

---

## How to change the city / weather location

The window already has a city menu (Сандански / София / Лондон).  
To add another city, edit `soul_gui.py` — the `self.cities` dictionary near the top of `SoulMonitor.__init__`.

If you are too lazy to do the changes yourself, ask for free help: **good.vibes.github@gmail.com**

You need three things per city:

1. Coordinates + timezone  
2. Display name  
3. freemeteo hourly-forecast URL

### 1. Coordinates + timezone

| City | Latitude | Longitude | Timezone |
| --- | --- | --- | --- |
| London, UK | 51.5074 | -0.1278 | Europe/London |
| New York, USA | 40.7128 | -74.0060 | America/New_York |
| Tokyo, Japan | 35.6762 | 139.6503 | Asia/Tokyo |
| Sofia, Bulgaria | 42.6977 | 23.3219 | Europe/Sofia |
| Sandanski, BG | 41.5667 | 23.2833 | Europe/Sofia |

Accurate coordinates: Google Maps or [Open-Meteo](https://open-meteo.com/).

Example entry:

```python
"Ню Йорк": {
    "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York",
    "fm": "https://freemeteo.bg/weather/new-york/hourly-forecast/today/?gid=5128581&language=bulgarian&country=united-states"
}
```

Then set the starting city:

```python
self.current_city = "Ню Йорк"
```

### 2. How to change the freemeteo hyperlink

At the bottom of the weather panel there is a clickable **freemeteo.bg** link.

1. Go to [https://freemeteo.bg](https://freemeteo.bg)
2. Search for your city
3. Open the **Hourly forecast** page for today
4. Copy the full URL
5. Put it in the `"fm"` field of that city

London example:

```text
https://freemeteo.co.uk/weather/london/hourly-forecast/today/?gid=2643743&language=english&country=united-kingdom
```

### 3. Day names (optional)

Forecast days are already in Bulgarian:

```python
bg_days = ["Пон", "Втор", "Сря", "Четв", "Пет", "Съб", "Нед"]
```

---

## The soul

Mood follows CPU + RAM load (and a “night” state when both are very low):

| State | When | Color |
| --- | --- | --- |
| night | CPU and RAM under 25% | cyan |
| calm | load under 35% | green |
| medium | load under 65% | gold |
| high | load under 85% | orange |
| critical | load 85%+ | red |

A short Bulgarian line is picked at random for the current mood.

---

## Tips

- Weather refreshes every **30 minutes** (`self.weather_interval = 1800`).
- The window stays **always-on-top** by default. Use the button to toggle it.
- Click the **clock / date** to open a 3-month calendar.
- Hardware temperatures come from `/sys/class/thermal/` — if the kernel does not export them, you will see `Темп: няма данни`.

---

## License

**Forever Free** for use by everyone: private and/or public and/or business.

You are free to use it as it is or change anything you want depending on your whims.

Any issues, questions, etc.:

**good.vibes.github@gmail.com**

Enjoy watching your computer's soul.
