# Beat Chopping

## Requirements

### System Libraries

```
sudo apt install aubio-tools portaudio19-dev
```

### Python Libraries

```
python3.7 -m venv env
env/bin/python -m pip install -U pip wheel
env/bin/python -m pip install -r requirements.txt
```

## Usage

```
env/bin/python -m chop [audiofile.wav] [OPTIONS ...]
```

To see a list of options, run the command with the `--help` argument.

For best results, use loopable, dry, percussion or drum samples, such as the
famouse "Amen Break".
