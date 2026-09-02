"""Synthesize clear Mandarin speech with Piper and play it with ALSA."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile


DEFAULT_PIPER_COMMAND = '~/.local/opt/piper/piper'
DEFAULT_MODEL_PATH = (
    '~/.local/share/piper/voices/zh_CN-huayan-medium.onnx'
)
DEFAULT_AUDIO_COMMAND = 'aplay'


def resolve_executable(command):
    """Resolve a command name or an explicit user-relative path."""
    expanded = os.path.expanduser(command)
    if os.path.sep in expanded:
        if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
            return expanded
        return None
    return shutil.which(expanded)


def dependency_errors(piper_command, model_path, audio_command):
    """Return actionable errors for missing Piper playback resources."""
    errors = []
    expanded_model = os.path.expanduser(model_path)
    if resolve_executable(piper_command) is None:
        errors.append(
            f'Piper executable not found: {os.path.expanduser(piper_command)}'
        )
    if not os.path.isfile(expanded_model):
        errors.append(f'Piper Chinese model not found: {expanded_model}')
    if not os.path.isfile(expanded_model + '.json'):
        errors.append(
            f'Piper model config not found: {expanded_model}.json'
        )
    if resolve_executable(audio_command) is None:
        errors.append(
            f'Audio player not found: {audio_command}; install alsa-utils'
        )
    return errors


def synthesize_and_play(
    text,
    piper_command=DEFAULT_PIPER_COMMAND,
    model_path=DEFAULT_MODEL_PATH,
    audio_command=DEFAULT_AUDIO_COMMAND,
):
    """Generate a temporary WAV with Piper, then play it synchronously."""
    errors = dependency_errors(
        piper_command, model_path, audio_command
    )
    if errors:
        raise RuntimeError('; '.join(errors))

    piper_executable = resolve_executable(piper_command)
    audio_executable = resolve_executable(audio_command)
    expanded_model = os.path.expanduser(model_path)
    with tempfile.TemporaryDirectory(
        prefix='elderly_voice_alarm_'
    ) as temporary_directory:
        wav_path = os.path.join(temporary_directory, 'alarm.wav')
        subprocess.run(
            [
                piper_executable,
                '--model',
                expanded_model,
                '--output_file',
                wav_path,
                '--quiet',
            ],
            input=text + '\n',
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        subprocess.run(
            [audio_executable, '-q', wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )


def _argument_parser():
    parser = argparse.ArgumentParser(
        description='Speak Simplified Chinese using offline Piper TTS.'
    )
    parser.add_argument('text', nargs='+', help='Chinese text to speak')
    parser.add_argument(
        '--piper-command', default=DEFAULT_PIPER_COMMAND
    )
    parser.add_argument('--model', default=DEFAULT_MODEL_PATH)
    parser.add_argument(
        '--audio-command', default=DEFAULT_AUDIO_COMMAND
    )
    return parser


def main(args=None):
    parsed = _argument_parser().parse_args(args)
    try:
        synthesize_and_play(
            ' '.join(parsed.text),
            piper_command=parsed.piper_command,
            model_path=parsed.model,
            audio_command=parsed.audio_command,
        )
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Piper Chinese TTS failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
