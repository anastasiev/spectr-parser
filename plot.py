import time

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import mplcursors
import datetime
import asyncio

import numpy as np

from helpers import channel2_wave_lengths

# plt.style.use('_mpl-gallery')
MAX_EXPO = 33

class SpectrPlot():
    def __init__(self, data):
        plt.ion()
        fig, ax = plt.subplots()
        fig.canvas.manager.set_window_title('Спектр')
        ax.set_position([0.05, 0.1, 0.85, 0.87])
        ax_slider = fig.add_axes([0.05, 0.01, 0.65, 0.03])
        ax_expo_slider = fig.add_axes([0.93, 0.15, 0.03, 0.65])
        slider = Slider(
            ax=ax_slider,
            label='Час',
            valmin=0,
            valstep=1,
            valmax=1
        )
        expo_slider = Slider(
            ax=ax_expo_slider,
            label='Експозиція',
            valmin=0,
            valstep=1,
            valmax=MAX_EXPO,
            orientation='vertical'
        )
        slider.valtext.set_text('')
        expo_slider.valtext.set_text('3 мс')
        expo_slider.set_active(False)
        ax_start = fig.add_axes([0.9, 0.01, 0.04, 0.03])
        ax_stop = fig.add_axes([0.95, 0.01, 0.04, 0.03])
        btn_start = Button(ax_start, 'Старт')
        btn_stop = Button(ax_stop, 'Стоп')
        btn_stop.set_active(False)
        btn_start.set_active(False)
        self.prev_ymin = 0
        self.prev_ymax = 100
        ax.set_ylim([self.prev_ymin, self.prev_ymax])
        self.btn_start = btn_start
        self.btn_stop = btn_stop
        self.ax = ax
        self.fig = fig
        self.slider = slider
        self.expo_slider = expo_slider
        self.data = data
        self.on_update_id = self.slider.on_changed(self.on_update_slider)
        self.on_update_expo_slider_id = self.expo_slider.on_changed(self.on_update_expo)
        self.line_ch1 = None
        self.line_ch2 = None
        self.exp_val = 0
        self.device_text = ax.text(0.3, 60, 'Прилад не підключений')
        fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def on_key_press(self, e):
        if self.data['started'] or self.data['terminated'] or not self.slider.get_active() or not self.expo_slider.get_active():
            return
        if e.key == 'left':
            if self.slider.val != self.slider.valmin:
                self.slider.set_val(self.slider.val - 1)
        elif e.key == 'right':
            if self.slider.val != self.slider.valmax:
                self.slider.set_val(self.slider.val + 1)
        elif e.key == 'up':
            if self.expo_slider.val != self.expo_slider.valmax:
                self.expo_slider.set_val(self.expo_slider.val + 1)
        elif e.key == 'down':
            if self.expo_slider.val != self.expo_slider.valmin:
                self.expo_slider.set_val(self.expo_slider.val - 1)


    def draw_plot(self, ch1, ch2):
        print('draw_plot')
        line_ch1, = self.ax.plot(ch1[0], ch1[1], c='b')
        line_ch2, = self.ax.plot(ch2[0], ch2[1], c='g')
        self.line_ch1 = line_ch1
        self.line_ch2 = line_ch2
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    @staticmethod
    def diff(val, prev_val):
        return abs(val - prev_val) / max(val, prev_val) > 0.1

    def scale_if_needed(self, ch1, ch2):
        full_data = ch1 + ch2
        ymin = min(full_data)
        ymax = max(full_data)
        if self.diff(ymin, self.prev_ymin) or self.diff(ymax, self.prev_ymax):
            offset = int(ymax * 0.05)
            self.prev_ymin = ymin
            self.prev_ymax = ymax
            self.ax.set_ylim([ymin - offset, ymax + offset])

    def handle_legend(self):
        current_frame = self.slider.val + 1
        self.line_ch1.set_label('Кадр ' + str(current_frame))
        self.line_ch2.set_label('')
        if self.exp_val != 0:
            from_val = current_frame - self.exp_val
            self.line_ch2.set_label('Експозиція з ' + str(from_val) + ' до ' + str(current_frame))
        self.ax.legend()

    async def redraw_plot(self):
        print('redraw_plot')
        data_frame = self.data['data_frames'][-1]
        ch1 = data_frame["values_ch1"]
        ch2 = data_frame["values_ch2"]
        self.line_ch1.set_ydata(ch1)
        self.line_ch2.set_ydata(ch2)
        ind = len(self.data['data_frames']) - 1
        self.slider.valmax = ind
        self.slider.ax.set_xlim(self.slider.valmin, self.slider.valmax)
        self.slider.set_val(ind)
        self.slider.valtext.set_text(data_frame["time"])
        self.scale_if_needed(ch1, ch2)
        self.handle_legend()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        await asyncio.sleep(0)

    def register_start(self, on_start):
        def handle(val):
            self.btn_start.set_active(False)
            self.btn_stop.set_active(True)
            self.slider.disconnect(self.on_update_id)
            self.expo_slider.disconnect(self.on_update_expo_slider_id)
            self.expo_slider.set_active(False)
            self.expo_slider.set_val(0)
            on_start()
        self.btn_start.on_clicked(handle)

    def register_close(self, on_close):
        def handler(e):
            plt.close('all')
            on_close()
        self.fig.canvas.mpl_connect('close_event', handler)

    def register_stop(self, on_stop):
        def handle(val):
            self.btn_start.set_active(True)
            self.btn_stop.set_active(False)
            self.on_update_id = self.slider.on_changed(self.on_update_slider)
            self.on_update_expo_slider_id = self.expo_slider.on_changed(self.on_update_expo)
            self.adjust_exp_slider()
            on_stop()
        self.btn_stop.on_clicked(handle)

    def show(self):
        plt.show()

    def wait_for_action(self):
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_update_slider(self, val):
        try:
            print("on change " + str(val))
            ch1, ch2, time_val = self.get_frame_data()
            self.slider.valtext.set_text(time_val)
            self.line_ch1.set_ydata(ch1)
            self.line_ch2.set_ydata(ch2)
            self.scale_if_needed(ch1, ch2)
            self.handle_legend()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        except:
            print('on time update error')
    def adjust_exp_slider(self):
        frames_number = len(self.data['data_frames'])
        if frames_number < MAX_EXPO:
            return
        self.expo_slider.set_val(0)
        self.expo_slider.set_active(True)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def get_frame_data(self):
        if self.exp_val == 0:
            frame = self.data['data_frames'][self.slider.val]
            return frame['values_ch1'], frame['values_ch2'], frame['time']
        current_ind = self.slider.val
        frames = self.data['data_frames'][current_ind - self.exp_val:current_ind + 1]
        time_val = self.data['data_frames'][current_ind - self.exp_val]['time']
        data_len = len(frames[0]['values_ch1'])
        ch1_sum_values = np.zeros(data_len)
        ch2_sum_values = np.zeros(data_len)
        for frame in frames:
            ch1_sum_values += np.array(frame['values_ch1'])
            ch2_sum_values += np.array(frame['values_ch2'])
        return ch1_sum_values.tolist(), ch2_sum_values.tolist(), time_val

    def on_update_expo(self, val):
        try:
            self.exp_val = val
            self.expo_slider.valtext.set_text('{} мс'.format(val * 3 + 3))
            ch1, ch2, time_val = self.get_frame_data()
            self.line_ch1.set_ydata(ch1)
            self.line_ch2.set_ydata(ch2)
            self.scale_if_needed(ch1, ch2)

            self.slider.valmin = 0 if self.exp_val == 0 else self.slider.valmax % self.exp_val
            self.slider.ax.set_xlim(self.slider.valmin, self.slider.valmax)
            self.slider.valtext.set_text(time_val)
            self.handle_legend()

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        except:
            print('on expo update error')


