from generativeai.roles.artisans.painter import Painter
from stablediffusion.sdapi import text_to_image_sd_api
from utils.log import info, debug
import random

PAINTER_SD_API = 'SDAPI'
__PAINTER_PROVIDER__ = 'stablediffusionapi.com'

class SdApiPainter(Painter):

    MODEL_MIDJOURNEY = "midjourney"
    MODEL_DELIBERATE = "deliberate-3"

    PARAM_SEED = 'seed'

    def __init__(self):
        super().__init__(PAINTER_SD_API, __PAINTER_PROVIDER__)

    def get_default_model(self):
        return SdApiPainter.MODEL_MIDJOURNEY

    def generate(self, prompt,
                 model=None,
                 width=1024, height=512,
                 **kwargs):
        composed_prompt = self.compose_prompt(prompt)
        debug("[{}] be asked to generate: {}".format(model, composed_prompt))
        if composed_prompt is None:
            return None

        seed = kwargs.pop(SdApiPainter.PARAM_SEED, random.randint(1, 99999))

        return text_to_image_sd_api(composed_prompt, model, width, height, seed)

