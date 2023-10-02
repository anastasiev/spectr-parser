from data import get_channel_values
from helpers import channel1_wave_lengths, channel2_wave_lengths
from influx import write_to_influx
# from plot import draw_plot, redraw_plot, add_frame, interactive_off, interactive_on
from plot import draw_plot, interactive_on, redraw_plot
from usb_spectr import get_data, parse_data, init_usb
import time
import datetime
import asyncio


global_data = {
    "data_frames": [],
    "current_index": -1,
    "line_ch1": None,
    "line_ch2": None
}

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
        max_ind = len(global_data["data_frames"]) - 1
        global_data["current_index"] = max_ind
        if ind == 10:
            await asyncio.sleep(0)
            ind = 0
        else:
            ind += 1
        # add_frame(ch1, ch2)


async def redraw():
    data_frame = global_data['data_frames'][-1]
    draw_plot((channel1_wave_lengths, data_frame["values_ch1"]),(channel2_wave_lengths, data_frame["values_ch2"]), global_data)

    while True:
        await redraw_plot(global_data)

if __name__ == '__main__':
    ioloop = asyncio.get_event_loop()

    interactive_on()
    asyncio.ensure_future(receive_data())
    asyncio.ensure_future(redraw())


    ioloop.run_forever()








