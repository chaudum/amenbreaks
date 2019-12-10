import argparse
import random
import sys
import time

import pyaudio
import wave

from aubio import source, onset

BUFFER_SIZE = 512
SLICE_SIZES = [1, 2, 4, 8]
STUTTER_SIZES = [4, 8, 16, 32]
WEIGHT = [2, 8, 6, 4]


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("audiofile")
    parser.add_argument("--onset-detection-method", "-o", default="mkl", choices={"energy", "hfc", "complex", "phase", "wphase", "specdiff", "kl", "mkl", "specflux"})
    parser.add_argument("--reverse-probability", "-r", default=0.7, type=float)
    parser.add_argument("--stutter-probability", "-s", default=0.9, type=float)
    return parser


def random_slices(onsets):
    """
    Generator yields slices in random order
    """
    while True:
        size = random.choices(SLICE_SIZES, WEIGHT, k=1)[0]
        length = len(onsets) - (1 + size)
        n = random.randint(0, length)
        slice = (onsets[n], onsets[n+size] - onsets[n])
        print("slice", n, slice)
        yield slice


def get_onsets(filename, method="default"):
    hop_size = BUFFER_SIZE // 2

    s = source(filename, 0, hop_size)
    samplerate = s.samplerate

    o = onset(method, BUFFER_SIZE, hop_size, samplerate)

    onsets = []
    while True:
        samples, read = s()
        if o(samples):
            onsets.append(o.get_last())
        if read < hop_size:
            break

    return onsets


def apply_stutter(data: bytes) -> bytes:
    d = bytes()
    m = random.choices(STUTTER_SIZES, WEIGHT, k=1)[0]
    for x in range(m):
        d += data[:len(data) // m]
    return d


def apply_reverse(data: bytes) -> bytes:
    return bytes(c for t in zip(data[0::2][::-1], data[1::2][::-1]) for c in t)


def read_slice(wf, sample_pos, duration_in_samples):
    wf.setpos(sample_pos)
    return wf.readframes(duration_in_samples * wf.getnchannels())


def main(args):
    onsets = get_onsets(args.audiofile, method=args.onset_detection_method)

    with wave.open(args.audiofile, 'rb') as wf:

        p = pyaudio.PyAudio()

        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )

        slices = random_slices(onsets)
        try:
            for sample_pos, duration_in_samples in slices:
                data = read_slice(wf, sample_pos, duration_in_samples)
                if random.random() > args.stutter_probability:
                    data = apply_stutter(data)
                if random.random() > args.reverse_probability:
                    data = apply_reverse(data)
                stream.write(data)
        except Exception as e:
            print(e)

        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
