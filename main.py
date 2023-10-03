from data import get_channel_values
from helpers import channel1_wave_lengths, channel2_wave_lengths
from influx import write_to_influx
# from plot import draw_plot, redraw_plot, add_frame, interactive_off, interactive_on
from plot import SpectrPlot
from usb_spectr import get_data, parse_data, init_usb
import time
import datetime
import asyncio
import random


global_data = {
    "data_frames": [],
    "started": False,
    "first_draw": True
}

plot = SpectrPlot(global_data)
ioloop = asyncio.get_event_loop()


class TaskRunner():
    def __init__(self):
        self.running_tasks = []

    def stop_tasks(self):
        for task in self.running_tasks:
            task.cancel()

    def start_task(self, task):
        self.running_tasks.append(asyncio.ensure_future(task()))


runner = TaskRunner()


async def receive_data():
    start = time.time()
    device, address, packet_size = init_usb()
    ind = 0
    while True:
        data = get_data(device, address, packet_size)
        ct = time.time()
        delta = ct - start
        print(delta)
        start = ct
        ch1, ch2 = parse_data(data)
        current_time = datetime.datetime.now()
        global_data["data_frames"].append({
            "values_ch1": ch1,
            "values_ch2": ch2,
            "time": current_time
        })
        if ind == 10:
            await asyncio.sleep(0)
            ind = 0
        else:
            ind += 1


def get_random_channel_data():
    if int(time.time()) % 4 == 0:
        return [random.randint(150, 300) * 5 for _ in range(1824)]
    return [random.randint(150, 300) for _ in range(1824)]


async def receive_mocked_data():
    ind = 0
    while global_data['started'] == True:
        print('receive_mocked_data')
        ch1 = get_random_channel_data()
        ch2 = get_random_channel_data()
        current_time = datetime.datetime.now()
        global_data["data_frames"].append({
            "values_ch1": ch1,
            "values_ch2": ch2,
            "time": current_time
        })
        max_ind = len(global_data["data_frames"]) - 1
        global_data["current_index"] = max_ind
        if ind == 10:
            await asyncio.sleep(0)
            ind = 0
        else:
            ind += 1


async def redraw():
    data_frame = global_data['data_frames'][-1]
    if global_data['first_draw']:
        plot.draw_plot((channel1_wave_lengths, data_frame["values_ch1"]),(channel2_wave_lengths, data_frame["values_ch2"]))
        global_data['first_draw'] = False

    while global_data['started']:
        await plot.redraw_plot()


async def wait_for_action():
    while not global_data['started']:
        plot.wait_for_action()


def on_start():
    global_data['started'] = True
    runner.stop_tasks()
    runner.start_task(receive_mocked_data)
    runner.start_task(redraw)


def on_stop():
    global_data['started'] = False
    runner.stop_tasks()
    runner.start_task(wait_for_action)


def on_close(e):
    runner.stop_tasks()
    exit(0)


if __name__ == '__main__':
    plot.register_start(on_start)
    plot.register_stop(on_stop)
    plot.register_close(on_close)
    plot.show()
    runner.start_task(wait_for_action)
    # asyncio.ensure_future(redraw(plot))

    ioloop.run_forever()








