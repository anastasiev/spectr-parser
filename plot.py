import time

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import mplcursors
import datetime
import asyncio

import numpy as np

from helpers import channel2_wave_lengths

# plt.style.use('_mpl-gallery')

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


# def update(val):
#     print("on change " + str(val))
#     frame = data["data_frames"][val]
#     slider.valtext.set_text(frame["time"])
#     data["line"].set_ydata(frame["values"])
#     fig.canvas.draw_idle()


def draw_plot(ch1, ch2, data):
    line_ch1, = ax.plot(ch1[0], ch1[1], c='b')
    line_ch2, = ax.plot(ch2[0], ch2[1], c='g')
    data["line_ch1"] = line_ch1
    data["line_ch2"] = line_ch2
    # current_time = datetime.datetime.now()
    # data["data_frames"].append({
    #     "values_ch1": ch1[1],
    #     "values_ch2": ch2[1],
    #     "time": current_time
    # })
    # data["current_index"] = 0
    # slider.valmin = 0
    # slider.valmax = 0
    # slider.set_val(0)
    # slider.valtext.set_text(current_time)

    # mng = plt.get_current_fig_manager()
    # mng.full_screen_toggle()
    # mng.flag_is_max = True
    # plt.tight_layout()
    mplcursors.cursor(hover=True)
    plt.show()


# def add_frame(ch1, ch2):
#     current_time = datetime.datetime.now()
#     data["data_frames"].append({
#         "values_ch1": ch1,
#         "values_ch2": ch2,
#         "time": current_time
#     })
#     max_ind = len(data["data_frames"]) - 1
#     data["current_index"] = max_ind
#     slider.valmax = max_ind
#     slider.ax.set_xlim(slider.valmin, slider.valmax)
#     slider.set_val(max_ind)
#     slider.valtext.set_text(current_time)
#     redraw_plot(ch1, ch2)

async def redraw_plot(data):
    data_frame = data['data_frames'][-1]
    data["line_ch1"].set_ydata(data_frame["values_ch1"])
    data["line_ch2"].set_ydata(data_frame["values_ch2"])
    ind = data["current_index"]
    slider.valmax = ind
    slider.ax.set_xlim(slider.valmin, slider.valmax)
    slider.set_val(ind)
    slider.valtext.set_text(data_frame["time"])
    await asyncio.sleep(0)
    fig.canvas.draw()
    fig.canvas.flush_events()



def interactive_on():
    plt.ion()
