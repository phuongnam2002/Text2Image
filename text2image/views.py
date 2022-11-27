from typing import Any
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import torch
# from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from diffusers import StableDiffusionPipeline
import os
import uuid
from .models import Log

if torch.cuda.is_available():       
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use the GPU:', torch.cuda.get_device_name(0))
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")

tokenizer_vi2en_vin = AutoTokenizer.from_pretrained("vinai/vinai-translate-vi2en", src_lang="vi_VN")
model_vi2en_vin = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-vi2en")
model_vi2en_vin.to(device)


def translate_vi2en_vin(vi_text: str, tokenizer_vi2en, model_vi2en) -> str:
    input_ids = tokenizer_vi2en(vi_text, return_tensors="pt").input_ids.to(device)
    output_ids = model_vi2en.generate(
        input_ids,
        do_sample=True,
        top_k=100,
        top_p=0.8,
        decoder_start_token_id=tokenizer_vi2en.lang_code_to_id["en_XX"],
        num_return_sequences=1,
    )
    en_text = tokenizer_vi2en.batch_decode(output_ids, skip_special_tokens=True)
    en_text = " ".join(en_text)
    return en_text

# model_vi2en_t5 = T5ForConditionalGeneration.from_pretrained("NlpHUST/t5-vi-en-small")
# tokenizer_vi2en_t5 = T5Tokenizer.from_pretrained("NlpHUST/t5-vi-en-small")
# model_vi2en_t5.to(device)

# def translate_vi2en_t5(vi_text: str, tokenizer_vi2en, model_vi2en) -> str:
#     tokenized_text = tokenizer_vi2en.encode(vi_text, return_tensors="pt").to(device)
#     model_vi2en.eval()
#     summary_ids = model_vi2en.generate(
#                         tokenized_text,
#                         max_length=256, 
#                         num_beams=5,
#                         repetition_penalty=2.5, 
#                         length_penalty=1.0, 
#                         early_stopping=True
#                     )
#     en_text = tokenizer_vi2en.decode(summary_ids[0], skip_special_tokens=True)
#     en_text = " ".join(en_text)
#     return en_text

artist = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", 
    torch_type=torch.float16,
    revision="fp16",
    use_auth_token="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"
)
artist = artist.to(device)

# Create your views here.
class IndexView(View):
    template_name = 'index.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.translator = model_vi2en_vin
        self.tokenizer = tokenizer_vi2en_vin
        self.translate_vi2en = translate_vi2en_vin
        self.artist = artist
        self.word_limit = 1000
        
    def get(self, request):
        context = {
            'image_url': os.path.join('/static', 'proptit.png')
        }
        return render(request,self.template_name, context=context)
    
    def post(self, request):
        desc = request.POST['desciption']
        
        vi_text = ' '.join(desc.split()[:self.word_limit])
        en_text = self.translate_vi2en(vi_text, self.tokenizer, self.translator)

        prompt = en_text
        image = self.artist(prompt).images[0]
        name_file = f'{uuid.uuid1()}.png'
        image.save(os.path.join('media', name_file))
        image_url = os.path.join('/media', name_file)


        Log.objects.create(vi_text = vi_text, en_text = en_text, image = name_file)

        data = {
            'en_text': en_text,
            'vi_text': vi_text,
            'image_url': image_url
        }
        return JsonResponse(data)