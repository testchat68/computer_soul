# The Computer's Soul

A lightweight, always-on-top system monitor with personality.

Please see the picture: Soul.jpg

It shows:

- Live CPU usage (per-thread graphs)
- Memory usage graph
- Hardware temperatures (where available)
- A 7-day weather forecast
- A big clock + date
- ASCII art + short poems that change according to system load ("the soul")

Default city is **London, UK**.

---

## Requirements

- Python 3.6+
- `tkinter` (usually included with Python on Linux)
- Linux (uses `/proc` and `/sys` for CPU, memory and temperatures)

Works best on Linux. On other systems the CPU/memory/temp parts may not work or will show limited data.

---

## How to run

Put the file: `soul_gui.py` into HOME folder

Right mouse button on file and choose **Options → Permissions** and check all **EXECUTION** boxes.

Now move the file: `Душата.desktop` on the Desktop and do the same:

Right mouse button on file and choose **Options → Permissions** and check all **EXECUTION** boxes.

That's it - now you can use the program.

---

## How to change the city / weather location

The weather is fetched from the free [Open-Meteo](https://open-meteo.com/) API.

Open `soul_gui.py` and find the method `_update_weather`.

You need to change **three things**:

### 1. Coordinates + timezone (the API call)

Find this block:

```python
url = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=51.5074&longitude=-0.1278&"
    "daily=temperature_2m_max,temperature_2m_min,weathercode&"
    "timezone=Europe/London&forecast_days=7&"
    "models=ecmwf_ifs025"
)
```

Replace:

- `latitude=...`
- `longitude=...`
- `timezone=...`

**Examples:**

| City              | Latitude  | Longitude  | Timezone          |
|-------------------|-----------|------------|-------------------|
| London, UK        | 51.5074   | -0.1278    | Europe/London     |
| New York, USA     | 40.7128   | -74.0060   | America/New_York  |
| Tokyo, Japan      | 35.6762   | 139.6503   | Asia/Tokyo        |
| Sofia, Bulgaria   | 42.6977   | 23.3219    | Europe/Sofia      |
| Sandanski, BG     | 41.5667   | 23.2833    | Europe/Sofia      |

You can get accurate coordinates from Google Maps or from the Open-Meteo website itself.

### 2. City name shown in the window

In the same method, change these two lines:

```python
self.weather_text.insert(tk.END, "London • 7 days\n", ("header", "center"))
```

and in the error case:

```python
self.weather_text.insert(tk.END, "London • no connection", "header")
```

Replace `"London"` with your city name.

### 3. Day names (optional)

The code already uses English short day names (`Mon`, `Tue`...).

If you want another language, edit the list:

```python
en_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
```

---

## How to change the freemeteo.bg hyperlink

At the bottom of the window there is a clickable link `freemeteo.bg` that opens the hourly forecast for the current city.

To change it:

1. Go to [https://freemeteo.bg](https://freemeteo.bg)
2. Search for your city
3. Open the **Hourly forecast** page for today
4. Copy the full URL from the browser address bar

Then open `soul_gui.py` and find this part:

```python
self.freemeteo_label.bind(
    "<Button-1>",
    lambda e: webbrowser.open(
        "https://freemeteo.bg/weather/london/hourly-forecast/today/?gid=2643743&language=bulgarian&country=united-kingdom"
    )
)
```

Replace the URL inside the quotes with the one you copied.

**Default (London):**

```
https://freemeteo.bg/weather/london/hourly-forecast/today/?gid=2643743&language=bulgarian&country=united-kingdom
```

---

## Tips

- The weather is updated every 30 minutes (you can change `self.weather_interval`).
- The window stays always-on-top by default. Click the button to toggle it.
- The "soul" (ASCII face + poem) changes color and mood according to CPU + RAM load.

Forever Free for use by everyone: private and/or public and/or business. 

You are free to use as it is or change anything you want depending on your whims.

Any issues, questions or if you are too lazy to do changes: **good.vibes.github@gmail.com**

Enjoy watching your computer's soul.
