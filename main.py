from data import get_channel_values
from helpers import channel1_wave_lengths, channel2_wave_lengths
from influx import write_to_influx
from plot import draw_plot, redraw_plot, add_frame, interactive_off, interactive_on
import time

# def get_influx_fields():
#     frame1_str = read_file('frame11.txt')
#     frame2_str = read_file('frame12.txt')
#     frame1_values = get_decimal_values(frame1_str)
#     channel2_values = frame1_values[:1749]
#
#     frame2_values = get_decimal_values(frame2_str)
#     frame2_values.reverse()
#     channel1_values = frame2_values[192:]
#     channel1_tail_values = frame1_values[-149:]
#     channel1_tail_values.reverse()
#
#     channel1_values = channel1_values + channel1_tail_values
#
#     influx_data = []
#
#     for index, val in enumerate(channel2_values):
#         influx_data.append({
#             "measurement": "spectr_data",
#             "fields": {
#                 "w_len": channel2_wave_lengths[index],
#                 "intensity": val
#             }
#         })
#
#     for index, val in enumerate(channel1_values):
#         influx_data.append({
#             "measurement": "spectr_data",
#             "fields": {
#                 "w_len": channel1_wave_lengths[index],
#                 "intensity": val
#             }
#         })
#
#     return influx_data


if __name__ == '__main__':
    interactive_on()
    ind = 1
    data = get_channel_values(f'frames/frame11.txt', f'frames/frame12.txt', )
    x = data["channel1"]["wave_len"]
    y = data["channel1"]["values"]
    draw_plot(x, y)
    influx_data = []
    while ind <= 8:
        influx_data = {}
        data = get_channel_values(f'frames/frame{ind}1.txt', f'frames/frame{ind}2.txt', )
        y = data["channel1"]["values"]
        add_frame(y)
        time.sleep(0.3)
        ind += 1
        if ind == 10:
            ind = 1
    interactive_off()








