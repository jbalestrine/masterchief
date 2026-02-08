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
            # record a per-job diagnostic log so we can debug import/load issues
            try:
                diag = Path(__file__).parent / 'data' / 'backups' / f'job_{job_id}.log'
                diag.parent.mkdir(parents=True, exist_ok=True)
                with diag.open('a', encoding='utf-8') as fh:
                    fh.write(f"--- {time.ctime()} ---\n")
                    fh.write('PIPELINE NOT AVAILABLE\n')
                    try:
                        import importlib, sys
                        fh.write('sys.path snapshot:\n')
                        for pth in sys.path[:5]:
                            fh.write('  ' + str(pth) + '\n')
                        fh.write('\n')
                        fh.write('torch spec: ' + str(importlib.util.find_spec('torch')) + '\n')
                        fh.write('diffusers spec: ' + str(importlib.util.find_spec('diffusers')) + '\n')
                    except Exception as ee:
                        fh.write('diag import failed: ' + str(ee) + '\n')
            except Exception:
                pass
            job['status'] = 'error'
            job['error'] = 'diffusers or torch not available on worker'
            job_path.write_text(json.dumps(job), encoding='utf-8')
            return

        job['progress'] = 15
        prompt = job.get('prompt','')
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
