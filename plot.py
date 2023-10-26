import time

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import datetime
import asyncio
import easygui
import pickle
import xlsxwriter

import numpy as np

from helpers import channel1_wave_lengths, channel2_wave_lengths

MAX_EXPO = 50
SPECTR_EXT = 'spectr'
EXCEL_EXT = 'xslx'

class SpectrPlot():
    def __init__(self, data):
        plt.ion()
        fig, ax = plt.subplots()
        fig.canvas.manager.set_window_title('Спектр')
        ax.set_position([0.05, 0.1, 0.85, 0.87])
        ax_slider = fig.add_axes([0.05, 0.01, 0.65, 0.03])
        ax_expo_slider = fig.add_axes([0.93, 0.15, 0.03, 0.35])
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
        expo_slider.valtext.set_text('18 мс')
        expo_slider.set_active(False)
        ax_start = fig.add_axes([0.92, 0.06, 0.07, 0.04])
        ax_stop = fig.add_axes([0.92, 0.01, 0.07, 0.04])
        btn_start = Button(ax_start, 'Старт')
        btn_stop = Button(ax_stop, 'Стоп')
        btn_stop.set_active(False)
        btn_start.set_active(False)
        ax_save = fig.add_axes([0.91, 0.9, 0.07, 0.04])
        ax_load = fig.add_axes([0.91, 0.82, 0.07, 0.04])
        btn_save = Button(ax_save, 'Зберегти')
        btn_save.set_active(False)
        btn_load = Button(ax_load, 'Відкрити')
        self.btn_save = btn_save
        self.btn_load = btn_load
        self.btn_save.on_clicked(self.on_save_btn)
        self.btn_load.on_clicked(self.on_load_btn)
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
        annot = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"))
        annot.set_visible(False)
        self.annot = annot
        self.scatter = None
        self.hover_event_id = None
        mpl.rcParams['keymap.back'].remove('left')
        mpl.rcParams['keymap.forward'].remove('right')
        fig.set_size_inches(16.5, 8.5)
        ax_export_all = fig.add_axes([0.91, 0.74, 0.07, 0.04])
        ax_export_current = fig.add_axes([0.91, 0.66, 0.07, 0.06])
        btn_export_all = Button(ax_export_all, 'Експорт')
        btn_export_current = Button(ax_export_current, 'Експорт\nПоточний')
        ax_scatter_switch = fig.add_axes([0.91, 0.58, 0.07, 0.06])
        self.switch_state = True
        scatter_visibility_switch = Button(ax_scatter_switch, 'Сховати\nТочки')

        scatter_visibility_switch.on_clicked(self.on_scatter_visibility_on_click)
        self.scatter_visibility_switch = scatter_visibility_switch
        self.btn_export_all = btn_export_all
        self.btn_export_current = btn_export_current
        self.btn_export_all.set_active(False)
        self.btn_export_current.set_active(False)
        self.btn_export_all.on_clicked(self.on_export_all_btn)
        self.btn_export_current.on_clicked(self.on_export_current_btn)

    def on_scatter_visibility_on_click(self, _):
        if self.scatter is None:
            return

        if self.switch_state:
            self.scatter_visibility_switch.label.set_text('Показати\nТочки')
            self.switch_state = False
            self.hide_scatter()
        else:
            self.scatter_visibility_switch.label.set_text('Сховати\nТочки')
            self.switch_state = True
            self.show_scatter()



    def update_annot(self, ind):
        pos = self.scatter.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        x = pos[0]
        y = pos[1]
        text = "д={}, і={}".format(x, int(y))
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.4)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_scatter_data(self):
        if self.scatter is not None:
            ch1_x = self.line_ch1.get_xdata()
            ch1_y = np.array(self.line_ch1.get_ydata())
            ch2_x = self.line_ch2.get_xdata()
            ch2_y = np.array(self.line_ch2.get_ydata())
            x = np.concatenate((ch1_x, ch2_x), axis=None).reshape((len(ch1_x)*2, 1))
            y = np.concatenate((ch1_y, ch2_y), axis=None).reshape((len(ch1_y)*2, 1))
            offsets = np.concatenate((x, y), axis=1)
            self.scatter.set_offsets(offsets)

    def on_save_btn(self, _):
        if self.data['data_frames'] is not None:
            file_to_save = easygui.filesavebox(filetypes=['\\*.{}'.format(SPECTR_EXT)])
            if file_to_save is None:
                return
            file_to_save = '{}.{}'.format(file_to_save, SPECTR_EXT)
            f = open(file_to_save, 'wb')
            pickle.dump(self.data['data_frames'], f)

    def on_load_btn(self, _):
        file_name = easygui.fileopenbox(default="~\\*.{}".format(SPECTR_EXT))
        if file_name is None:
            return
        data_frames = pickle.load(open(file_name, 'rb'))
        self.data['data_frames'] = data_frames
        data_frame = self.data['data_frames'][-1]
        ch1_val = data_frame["values_ch1"]
        ch2_val = data_frame["values_ch2"]
        if self.line_ch1 is None and self.line_ch2 is None:
            self.draw_plot((channel1_wave_lengths, ch1_val), (channel2_wave_lengths, ch2_val))
            self.line_ch1.set_ydata(ch1_val)
            self.line_ch2.set_ydata(ch1_val)
            self.show_scatter()
            self.data['first_draw'] = False

        self.line_ch1.set_ydata(ch1_val)
        self.line_ch2.set_ydata(ch1_val)

        ind = len(data_frames) - 1
        self.slider.valmax = ind
        self.slider.ax.set_xlim(self.slider.valmin, self.slider.valmax)
        self.slider.set_val(ind)
        self.slider.valtext.set_text(data_frame["time"])

        self.scale_if_needed(ch1_val, ch2_val)

        self.btn_save.set_active(True)
        self.btn_load.set_active(True)
        self.slider.set_active(True)
        self.btn_export_all.set_active(True)
        self.btn_export_current.set_active(True)
        self.adjust_exp_slider()
        self.handle_legend()
        self.device_text.set_text('')

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_export_all_btn(self, _):
        file_to_save = easygui.filesavebox(filetypes=['\\*.{}'.format(EXCEL_EXT)])
        if file_to_save is None:
            return
        file_to_save = '{}.{}'.format(file_to_save, EXCEL_EXT)
        workbook = xlsxwriter.Workbook(file_to_save)
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'bold': True, 'text_wrap': True})

        for cell, wave in enumerate(channel1_wave_lengths, start=1):
            worksheet.write(cell, 0, wave, cell_format)

        start_cell = len(channel1_wave_lengths) + 1
        for cell, wave in enumerate(channel2_wave_lengths, start=start_cell):
            worksheet.write(cell, 0, wave, cell_format)

        data_frames = self.data['data_frames']
        for frame_count, frames in enumerate(data_frames, start=1):
            ch1_values = frames["values_ch1"]
            ch2_values = frames["values_ch2"]
            frame_time = frames["time"]

            worksheet.write(0, frame_count, 'Час {}\nКадр {}'.format(frame_time, frame_count), cell_format)

            for cell, val in enumerate(ch1_values, start=1):
                worksheet.write(cell, frame_count, val)

            for cell, val in enumerate(ch2_values, start=start_cell):
                worksheet.write(cell, frame_count, val)

        worksheet.set_column(1, len(data_frames), 30)
        worksheet.set_row(0, 45)
        workbook.close()

    def on_export_current_btn(self, _):
        file_to_save = easygui.filesavebox(filetypes=['\\*.{}'.format(EXCEL_EXT)])
        if file_to_save is None:
            return
        file_to_save = '{}.{}'.format(file_to_save, EXCEL_EXT)
        workbook = xlsxwriter.Workbook(file_to_save)
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'bold': True, 'text_wrap': True})

        for cell, wave in enumerate(channel1_wave_lengths, start=1):
            worksheet.write(cell, 0, wave, cell_format)

        start_cell = len(channel1_wave_lengths) + 1
        for cell, wave in enumerate(channel2_wave_lengths, start=start_cell):
            worksheet.write(cell, 0, wave, cell_format)

        ch1_values = self.line_ch1.get_ydata()
        ch2_values = self.line_ch2.get_ydata()

        frame_number_str = self.line_ch1.get_label()
        expo_str = self.line_ch2.get_label()

        header_str = frame_number_str if expo_str == '' else '{}\n{}'.format(frame_number_str,expo_str)

        worksheet.write(0, 1, header_str, cell_format)

        for cell, val in enumerate(ch1_values, start=1):
            worksheet.write(cell, 1, val)

        for cell, val in enumerate(ch2_values, start=start_cell):
            worksheet.write(cell, 1, val)

        worksheet.set_column(1, 1, 20)
        worksheet.set_row(0, 45)
        workbook.close()

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
        self.update_scatter_data()
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
            self.slider.set_active(False)
            self.slider.disconnect(self.on_update_id)
            self.expo_slider.disconnect(self.on_update_expo_slider_id)
            self.expo_slider.set_active(False)
            self.expo_slider.set_val(0)
            self.btn_save.set_active(False)
            self.btn_load.set_active(False)
            self.btn_export_all.set_active(False)
            self.btn_export_current.set_active(False)
            self.hide_scatter()
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
            self.btn_save.set_active(True)
            self.btn_load.set_active(True)
            self.slider.set_active(True)
            self.btn_export_all.set_active(True)
            self.btn_export_current.set_active(True)
            self.on_update_id = self.slider.on_changed(self.on_update_slider)
            self.on_update_expo_slider_id = self.expo_slider.on_changed(self.on_update_expo)
            self.show_scatter()
            self.adjust_exp_slider()
            self.on_save_btn(None)
            on_stop()

        self.btn_stop.on_clicked(handle)

    def show_scatter(self):
        if self.scatter is None:
            self.scatter = self.ax.scatter(
                np.concatenate((self.line_ch1.get_xdata(), self.line_ch2.get_xdata()), axis=None),
                self.line_ch1.get_ydata() + self.line_ch2.get_ydata(),
                c='red', s=8
            )
        else:
            self.scatter.set_visible(True)
        self.hover_event_id = self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def hide_scatter(self):
        if self.scatter is not None:
            self.scatter.set_visible(False)
            self.fig.canvas.mpl_disconnect(self.hover_event_id)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def on_hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.scatter.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()

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
            self.update_scatter_data()
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
            self.expo_slider.valtext.set_text('{} мс'.format(val * 18 + 18))
            ch1, ch2, time_val = self.get_frame_data()
            self.line_ch1.set_ydata(ch1)
            self.line_ch2.set_ydata(ch2)
            self.update_scatter_data()
            self.scale_if_needed(ch1, ch2)

            self.slider.valmin = 0 if self.exp_val == 0 else self.slider.valmax % self.exp_val
            self.slider.ax.set_xlim(self.slider.valmin, self.slider.valmax)
            self.slider.valtext.set_text(time_val)
            self.handle_legend()

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        except:
            print('on expo update error')


