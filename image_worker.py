#!/usr/bin/env python3
"""Background image worker: processes JSON job files placed in data/image_jobs.

Usage: python image_worker.py

This worker lazily loads diffusers/torch when it processes the first job, so the main web
process doesn't import heavy libraries unless the worker runs.
"""
import time
import json
import os
import uuid
import traceback
from pathlib import Path

JOBS_DIR = Path(__file__).parent / 'data' / 'image_jobs'
OUT_DIR = Path(__file__).parent / 'data' / 'echo_images'
JOBS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

PIPELINE = None
MODEL_ID = os.environ.get('IMAGE_LOCAL_MODEL', 'runwayml/stable-diffusion-v1-5')

# Style -> prompt suffix mapping so the selected style actually affects generation
_STYLE_SUFFIXES = {
    'photorealistic': ', photorealistic, hyperrealistic, 8k uhd, sharp focus, dslr photography, highly detailed',
    'illustration':   ', illustration, artistic, detailed painting, vibrant colors, smooth linework',
    'digital-art':    ', digital art, concept art, vivid colors, artstation, trending, cinematic lighting',
}


def _build_prompt(job: dict) -> str:
    """Return the prompt with the chosen style suffix appended."""
    base   = (job.get('prompt') or '').strip()
    style  = (job.get('style')  or '').strip().lower()
    suffix = _STYLE_SUFFIXES.get(style, '')
    return base + suffix


def load_pipeline():
    global PIPELINE
    if PIPELINE is not None:
        return PIPELINE
    try:
        # Temporarily ensure the standard library is importable even if the repo
        # contains a local package named `platform` which would shadow the stdlib.
        import sys
        repo_dir = Path(__file__).resolve().parent
        removed = False
        repo_str = str(repo_dir)
        if repo_str in sys.path:
            try:
                sys.path.remove(repo_str)
                removed = True
            except Exception:
                removed = False

        try:
            import torch
            from diffusers import StableDiffusionPipeline
            print('Loading pipeline:', MODEL_ID)
            PIPELINE = StableDiffusionPipeline.from_pretrained(MODEL_ID)
            return PIPELINE
        finally:
            if removed:
                # put repo back on sys.path at its original front
                try:
                    sys.path.insert(0, repo_str)
                except Exception:
                    pass
    except Exception as e:
        try:
            import traceback
            tb = traceback.format_exc()
            errdir = Path(__file__).parent / 'data' / 'backups'
            errdir.mkdir(parents=True, exist_ok=True)
            errfile = errdir / 'pipeline_error.log'
            with errfile.open('a', encoding='utf-8') as fh:
                fh.write(f"--- {time.ctime()} ---\n")
                fh.write(tb)
                fh.write('\n')
        except Exception:
            pass
        print('Failed to load pipeline:', e)
        PIPELINE = None
        return None


def process_job(job_path: Path):
    try:
        job = json.loads(job_path.read_text(encoding='utf-8'))
    except Exception as e:
        print('Invalid job file, skipping:', job_path, e)
        return
    job_id = job.get('id')
    try:
        job['status'] = 'running'
        job['progress'] = 5
        job_path.write_text(json.dumps(job), encoding='utf-8')

        pipe = load_pipeline()
        if pipe is None:
            # Diffusers/torch unavailable — fall back to PIL placeholder image
            try:
                from PIL import Image, ImageDraw, ImageFont
                import textwrap
                prompt_text = _build_prompt(job)
                size_str = job.get('size', '512x512')
                try:
                    w, h = (int(x) for x in size_str.split('x'))
                except Exception:
                    w, h = 512, 512
                img = Image.new('RGB', (w, h), color=(30, 20, 50))
                draw = ImageDraw.Draw(img)
                # purple gradient-ish background bands
                for y in range(h):
                    r = int(20 + (y / h) * 40)
                    g = int(10 + (y / h) * 20)
                    b = int(50 + (y / h) * 60)
                    draw.line([(0, y), (w, y)], fill=(r, g, b))
                # border
                draw.rectangle([4, 4, w - 5, h - 5], outline=(150, 100, 220), width=3)
                # title
                try:
                    font_title = ImageFont.truetype('arial.ttf', 22)
                    font_body = ImageFont.truetype('arial.ttf', 16)
                except Exception:
                    font_title = ImageFont.load_default()
                    font_body = font_title
                draw.text((w // 2, 30), '🖼️ Echo Image Preview', font=font_title, fill=(220, 200, 255), anchor='mm')
                draw.text((w // 2, 60), '(diffusers not installed — placeholder)', font=font_body, fill=(160, 140, 200), anchor='mm')
                # wrapped prompt
                max_chars = max(20, w // 10)
                lines = textwrap.wrap(prompt_text, width=max_chars)
                y_pos = h // 2 - len(lines) * 18
                for line in lines:
                    draw.text((w // 2, y_pos), line, font=font_body, fill=(255, 240, 255), anchor='mm')
                    y_pos += 28
                # footer hint
                draw.text((w // 2, h - 30), 'pip install diffusers[torch] transformers', font=font_body, fill=(120, 100, 160), anchor='mm')
                fname = f"img_{int(time.time()*1000)}_{uuid.uuid4().hex}.png"
                fpath = OUT_DIR / fname
                img.save(str(fpath))
                rel = fpath.relative_to(Path(__file__).parent).as_posix()
                job['path'] = rel
                job['progress'] = 100
                job['status'] = 'done'
                job_path.write_text(json.dumps(job), encoding='utf-8')
                print('Job done (PIL placeholder):', job_id, '->', rel)
            except Exception as pil_err:
                job['status'] = 'error'
                job['error'] = f'diffusers/torch not available; PIL fallback also failed: {pil_err}'
                job_path.write_text(json.dumps(job), encoding='utf-8')
            return

        job['progress'] = 15
        prompt = _build_prompt(job)
        size = job.get('size','512x512')
        parts = size.split('x')
        try:
            width = int(parts[0]); height = int(parts[1])
        except Exception:
            width = 512; height = 512

        num_steps = 20

        def _cb(step, timestep, latents):
            try:
                pct = 30 + int((step / max(1, num_steps)) * 60)
                job['progress'] = min(95, pct)
                job_path.write_text(json.dumps(job), encoding='utf-8')
            except Exception:
                pass

        try:
            out = pipe(prompt, height=height, width=width, num_inference_steps=num_steps, callback=_cb, callback_steps=1)
        except TypeError:
            out = pipe(prompt, height=height, width=width, num_inference_steps=num_steps)

        image = out.images[0]
        fname = f"img_{int(time.time()*1000)}_{uuid.uuid4().hex}.png"
        fpath = OUT_DIR / fname
        image.save(str(fpath))
        rel = fpath.relative_to(Path(__file__).parent).as_posix()
        job['path'] = rel
        job['progress'] = 100
        job['status'] = 'done'
        job_path.write_text(json.dumps(job), encoding='utf-8')
        print('Job done:', job_id, '->', rel)
    except Exception as e:
        print('Job error', job_id, e)
        job['status'] = 'error'
        job['error'] = str(e) + '\n' + traceback.format_exc()
        try:
            job_path.write_text(json.dumps(job), encoding='utf-8')
        except Exception:
            pass


def main():
    print('Starting image worker, watching', JOBS_DIR)
    try:
        while True:
            try:
                # heartbeat for debugging: write a small timestamp so external monitors
                # can see the worker is alive even if stdout is not captured.
                try:
                    hb = Path(__file__).parent / 'data' / 'backups' / 'worker_heartbeat.log'
                    hb.parent.mkdir(parents=True, exist_ok=True)
                    with hb.open('a', encoding='utf-8') as fh:
                        fh.write(time.ctime() + '\n')
                except Exception:
                    pass

                for p in sorted(JOBS_DIR.glob('*.json')):
                    try:
                        j = json.loads(p.read_text(encoding='utf-8'))
                    except Exception:
                        continue
                    status = j.get('status')
                    if status in (None, 'queued', 'pending', 'claimed'):
                        # claim and process
                        j['status'] = 'claimed'
                        p.write_text(json.dumps(j), encoding='utf-8')
                        process_job(p)
                time.sleep(2)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print('Worker loop error:', e)
                time.sleep(5)
    except KeyboardInterrupt:
        print('Worker interrupted')


if __name__ == '__main__':
    main()
