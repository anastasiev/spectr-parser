from helpers import channel1_wave_lengths, channel2_wave_lengths
from plot import SpectrPlot
from usb_spectr import get_data, parse_data, init_usb, lookup_device
import time
import datetime
import asyncio
import random


global_data = {
    "data_frames": [],
    "started": False,
    "first_draw": True,
    "terminated": False,
    "device": None,
    "address": None,
    "packet_size": None
}

plot = SpectrPlot(global_data)
ioloop = asyncio.get_event_loop()

class TaskRunner:
    def __init__(self):
        self.running_tasks = []

    def stop_tasks(self):
        for task in self.running_tasks:
            task.cancel()
        self.running_tasks = []

    def start_task(self, task):
        self.running_tasks.append(asyncio.ensure_future(task()))


runner = TaskRunner()


async def receive_data():
    start = time.time()
    while global_data['device'] is None:
        try:
            device, address, packet_size = init_usb()
            global_data['device'] = device
            global_data['address'] = address
            global_data['packet_size'] = packet_size
        except Exception as e:
            print(str(e))

    ind = 0
    while global_data['started'] and not global_data['terminated']:
        data = get_data(global_data['device'], global_data['address'], global_data['packet_size'])
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


async def receive_data_mocked():
    ind = 0
    while global_data['started'] and not global_data['terminated']:
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
    if global_data['first_draw']:
        data_frame = global_data['data_frames'][-1]
        plot.draw_plot((channel1_wave_lengths, data_frame["values_ch1"]),(channel2_wave_lengths, data_frame["values_ch2"]))
        global_data['first_draw'] = False

    while global_data['started'] and not global_data['terminated']:
        await plot.redraw_plot()


async def wait_for_action():
    while not global_data['started'] and not global_data['terminated']:
        plot.wait_for_action()
        await asyncio.sleep(0)


async def looking_for_device():
    device = lookup_device()
    while device is None and not global_data['terminated']:
        print('Not Found')
        await asyncio.sleep(1)
        device = lookup_device()

    print('Found')
    plot.device_text.set_text('')
    plot.btn_start.set_active(True)


async def looking_for_device_mocked():
    print('Found')
    plot.device_text.set_text('')
    plot.btn_start.set_active(True)


def on_start():
    global_data['started'] = True


def on_stop():
    global_data['started'] = False


def on_close():
    global_data['terminated'] = True


async def main():
    plot.register_start(on_start)
    plot.register_stop(on_stop)
    plot.register_close(on_close)
    plot.show()
    await asyncio.gather(wait_for_action(), looking_for_device())
    while not global_data['terminated']:
        await asyncio.gather(receive_data(), redraw())
        await wait_for_action()


if __name__ == '__main__':
    asyncio.run(main())





