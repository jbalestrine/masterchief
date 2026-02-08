import traceback
import sys
try:
    from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import StableDiffusionPipeline
    print('Imported pipeline ok')
except Exception:
    traceback.print_exc()
    sys.exit(2)
else:
    sys.exit(0)
