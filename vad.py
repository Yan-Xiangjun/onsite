from silero_vad import load_silero_vad, read_audio, get_speech_timestamps

model = load_silero_vad(onnx=True)


def speech_is_end(path):
    wav = read_audio(path)
    out = get_speech_timestamps(
        wav,
        model,
        return_seconds=True,  # Return speech timestamps in seconds (default is samples)
    )

    if len(out) == 0:
        return True
    else:
        return False


if __name__ == '__main__':
    print(speech_is_end('./vad.wav'))
