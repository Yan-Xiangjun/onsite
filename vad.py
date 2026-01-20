from silero_vad import load_silero_vad, read_audio, get_speech_timestamps

model = load_silero_vad(onnx=True)


def is_speech(path):
    wav = read_audio(path)
    out = get_speech_timestamps(
        wav,
        model,
        return_seconds=True,  # Return speech timestamps in seconds (default is samples)
    )

    if len(out) == 0:
        return False
    else:
        return True


if __name__ == '__main__':
    import time
    t1 = time.time()
    print(is_speech('./vad.wav'))
    print(time.time() - t1)
