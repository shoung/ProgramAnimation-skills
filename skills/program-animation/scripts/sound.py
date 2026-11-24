"""Synthesize a timed score, Foley cues and reviewed narration into a PCM WAV."""

import argparse
import json
import math
import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

RATE = 24000
CATEGORIES = ("polyphones", "names", "numbers")


def validate(plan):
    duration = plan["duration"]
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration must be positive")
    prior = -1
    for cue in plan.get("narration", []):
        if not prior < cue["at"] < duration or cue["at"] < 0:
            raise ValueError("Narration start times must increase within the film")
        prior = cue["at"]
        if not cue["text"].strip() or not cue["spoken"].strip():
            raise ValueError("Both display text and reviewed TTS text are required")
        for category in CATEGORIES:
            entries = cue["readings"].get(category)
            if not isinstance(entries, list):
                raise TypeError(f"Review {category} before synthesis (use [] when absent)")
            for entry in entries:
                if not entry["term"] or entry["term"] not in cue["text"] or not entry["as"].strip():
                    raise ValueError(f"Reading must identify a source term and its intended sound: {entry}")
    for fx in plan.get("effects", []):
        if fx["kind"] not in {"surf", "bell", "tap"}:
            raise ValueError(f"Unknown effect: {fx['kind']}")
        if fx["at"] < 0 or fx["seconds"] <= 0 or fx["at"] + fx["seconds"] > duration + 1e-9:
            raise ValueError(f"Effect outside timeline: {fx}")
    music = plan.get("music")
    if music and (
        music["beat_seconds"] <= 0
        or not music["chords"]
        or any(not chord or min(chord) <= 0 for chord in music["chords"])
    ):
        raise ValueError("Music requires a positive beat length and chords of positive frequencies")


def voice(cue, work, engine, name):
    source = work / "input.txt"
    source.write_text(cue["spoken"], encoding="utf-8")
    if engine == "say":
        file = work / "voice.aiff"
        subprocess.run(["say", "-v", name, "-o", str(file), "-f", str(source)], check=True)
    else:
        file = work / "voice.wav"
        subprocess.run(["espeak-ng", "-v", name, "-w", str(file), "-f", str(source)], check=True)
    result = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-xerror",
            "-i",
            str(file),
            "-f",
            "f32le",
            "-ar",
            str(RATE),
            "-ac",
            "1",
            "pipe:1",
        ]
    )
    samples = np.frombuffer(result, dtype="<f4")
    voiced = np.flatnonzero(np.abs(samples) > 0.002)
    if not len(voiced):
        raise RuntimeError("TTS returned silent audio")
    # Preserve release and breathing room, discard redundant engine tail padding.
    return samples[: voiced[-1] + 1 + round(0.12 * RATE)]


def music_bed(length, music):
    bed = np.zeros(length, dtype=np.float32)
    if not music:
        return bed
    beat = music["beat_seconds"]
    for j in range(math.ceil(length / (RATE * beat))):
        start = round(j * beat * RATE)
        n = min(round(beat * 2 * RATE), length - start)
        if n <= 0:
            continue
        t = np.arange(n) / RATE
        chord = music["chords"][(j // 4) % len(music["chords"])]
        pitch = chord[j % len(chord)]
        tone = np.sin(math.tau * pitch * t) + 0.23 * np.sin(math.tau * 2 * pitch * t)
        env = (
            (1 - np.exp(-t * 28))
            * np.exp(-t / (beat * 0.72))
            * np.minimum(1, (n - np.arange(n)) / (RATE * 0.04))
        )
        bed[start : start + n] += music.get("gain", 0.13) * env * tone
    return bed


def mix(plan, output, engine=None, name=None):
    validate(plan)  # Finish semantic review for every cue before invoking any speech engine.
    count = round(plan["duration"] * RATE)
    music = music_bed(count, plan.get("music"))
    speech = np.zeros(count, dtype=np.float32)
    duck = np.ones(count, dtype=np.float32)
    rng = np.random.default_rng(551)
    for effect in plan.get("effects", []):
        start = round(effect["at"] * RATE)
        n = min(round(effect["seconds"] * RATE), count - start)
        t = np.arange(n) / RATE
        if effect["kind"] == "surf":
            noise = np.convolve(rng.normal(size=n), np.ones(17) / 4.1, mode="full")[:n]
            signal = noise * np.sin(np.pi * np.arange(n) / max(1, n)) ** 2
        elif effect["kind"] == "bell":
            hz = effect.get("hz", 710)
            signal = (np.sin(math.tau * hz * t) + 0.32 * np.sin(math.tau * hz * 2.71 * t)) * np.exp(
                -t * 4.7
            )
        else:
            signal = rng.normal(size=n) * np.exp(-t * 60)
        release = np.minimum(1, (n - np.arange(n)) / (RATE * 0.012))
        music[start : start + n] += signal * release * effect.get("gain", 0.1)
    report = []
    cues = plan.get("narration", [])
    if cues:
        engine = engine or ("say" if shutil.which("say") else "espeak-ng")
        if not shutil.which(engine):
            raise RuntimeError(f"Install the {engine} speech engine or use another voice renderer")
        name = name or ("Meijia" if engine == "say" else "cmn")
    with tempfile.TemporaryDirectory() as folder:
        for i, cue in enumerate(cues):
            samples = voice(cue, Path(folder), engine, name)
            start = round(cue["at"] * RATE)
            end = start + len(samples)
            limit = round(cues[i + 1]["at"] * RATE) if i + 1 < len(cues) else count
            if end > limit:
                raise ValueError(
                    f"Narration at {cue['at']} s ends at {end / RATE:.2f} s, past the next cue or film end"
                )
            speech[start:end] = samples * (0.76 / np.max(np.abs(samples)))
            ramp = min(round(0.12 * RATE), len(samples) // 2)
            gain = np.full(len(samples), 0.35)
            if ramp:
                gain[:ramp] = np.linspace(1, 0.35, ramp)
                gain[-ramp:] = np.linspace(0.35, 1, ramp)
            duck[start:end] = gain
            notes = [
                entry for group in CATEGORIES for entry in cue["readings"][group] if entry.get("listen")
            ]
            report.append(
                {
                    "start": start / RATE,
                    "end": round(end / RATE, 3),
                    "text": cue["text"],
                    "spoken": cue["spoken"],
                    "listen": notes,
                }
            )
    result = speech + music * duck
    result *= min(1, 0.94 / max(0.00001, float(np.max(np.abs(result)))))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as folder:
        temp = Path(folder) / "mix.wav"
        with wave.open(str(temp), "wb") as audio:
            audio.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
            audio.writeframes((result * 32767).astype("<i2").tobytes())
        os.replace(temp, output)
    return {"duration": count / RATE, "voice": name, "cues": report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--engine", choices=["say", "espeak-ng"])
    parser.add_argument("--voice")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    data = json.loads(args.plan.read_text(encoding="utf-8"))
    result = json.dumps(mix(data, args.out, args.engine, args.voice), ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(result + "\n", encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
