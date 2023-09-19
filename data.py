from helpers import channel2_wave_lengths, channel1_wave_lengths


def read_file(filename):
    with open(filename) as f:
        return f.readlines()[0]


def get_decimal_values(frame_str):
    hex_arr = [frame_str[i:i+4] for i in range(0, len(frame_str), 4)]
    return [int.from_bytes(bytes.fromhex(hex_val), byteorder='little') for hex_val in hex_arr]


def get_channel_values(frame1_filename = 'frame1.txt', frame2_filename = 'frame2.txt'):
    frame1_str = read_file(frame1_filename)
    frame2_str = read_file(frame2_filename)
    frame1_values = get_decimal_values(frame1_str)
    channel2_values = frame1_values[:1749]

    frame2_values = get_decimal_values(frame2_str)
    frame2_values.reverse()
    channel1_values = frame2_values[192:]
    channel1_tail_values = frame1_values[-149:]
    channel1_tail_values.reverse()
    channel1_values = channel1_values + channel1_tail_values
    return {
        "channel1" :{
            "values": channel1_values,
            "wave_len": channel1_wave_lengths[:len(channel1_values)]
        },
        "channel2": {
            "values": channel2_values,
            "wave_len": channel2_wave_lengths[:len(channel2_values)]
        }
    }
