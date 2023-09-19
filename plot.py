import time

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import mplcursors
import datetime

import numpy as np

from helpers import channel2_wave_lengths

# plt.style.use('_mpl-gallery')
data = {
    "data_frames": [],
    "current_index": -1,
    "line": None
}

fig, ax = plt.subplots()
ax.set_position([0.05, 0.07, 0.9, 0.9])
axslider = fig.add_axes([0.1, 0.01, 0.65, 0.03])
current_epoch = time.time_ns()
slider = Slider(
    ax=axslider,
    label='Time frame',
    valmin=0,
    valstep=1,
    valmax=1
)
slider.valtext.set_text('')


def update(val):
    print("on change " + str(val))
    frame = data["data_frames"][val]
    slider.valtext.set_text(frame["time"])
    data["line"].set_ydata(frame["values"])
    fig.canvas.draw_idle()


def draw_plot(x, y):
    line1, = ax.plot(x, y, c='b')
    data["line"] = line1
    current_time = datetime.datetime.now()
    data["data_frames"].append({
        "values": y,
        "time": current_time
    })
    data["current_index"] = 0
    slider.valmin = 0
    slider.valmax = 0
    slider.set_val(0)
    slider.valtext.set_text(current_time)
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    # plt.tight_layout()
    mplcursors.cursor(hover=True)
    plt.show()

    # plt.xlabel("Wave len")
    # plt.ylabel("Intension")
    # plt.plot(x, y, c='b')
    # mng = plt.get_current_fig_manager()
    # mng.full_screen_toggle()
    # plt.tight_layout()
    # mplcursors.cursor(hover=True)
    # plt.show()


def add_frame(y):
    current_time = datetime.datetime.now()
    data["data_frames"].append({
        "values": y,
        "time": current_time
    })
    max_ind = len(data["data_frames"]) - 1
    data["current_index"] = max_ind
    slider.valmax = max_ind
    slider.ax.set_xlim(slider.valmin, slider.valmax)
    slider.set_val(max_ind)
    slider.valtext.set_text(current_time)
    redraw_plot(y)


def redraw_plot(y):
    data["line"].set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()
    # fig.canvas.draw_idle()


def interactive_on():
    plt.ion()


def interactive_off():
    plt.ioff()
    slider.on_changed(update)
    # max_ind = len(data["data_frames"]) - 1
    # data["current_index"] = max_ind
    # slider.valmax = max_ind
    # slider.set_val(max_ind)
    plt.show()