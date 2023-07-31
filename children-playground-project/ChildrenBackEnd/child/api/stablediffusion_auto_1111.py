import random
import requests
import io
import base64
from PIL import Image, PngImagePlugin

# 데이터베이스 short int 범위 최대치
INF = 32767

class StableDiffusionAuto1111:
    def __init__(self, lora=None, model=None, vae=None):
        self._lora = lora
        self._model = model
        self._vae = vae
        self._end_point = "https://3660ab4c563d8f8763.gradio.live"
        self._save_path = "/Users/itstime/children-playground/children-playground-project/ChildrenFrontEnd/src/generatedImages"
        self._payload = {
            "restore_faces": True,
            "prompt": None,
            "negative_prompt": None,
            "batch_size": 1,
            "steps": None,
            "cfg_scale": None,
            "width": 512,
            "height": 768,
            "sampler_index": "DPM++ 2M"
        }
        
        self._option_payload = {
            "sd_model_checkpoint": None,
            "CLIP_stop_at_last_layers": 2,
            "sd_lora": None,
            "sd_vae": None,
        }

        # self._override_settings = {'sd_model_checkpoint' : "", 'filter_nsfw' : True}

    # 이미지 얻기
    # 이미지를 얻기 위해서 어떤 모델을 사용할지 받아오고
    # 1. 그 모델로 체인지 로라면 로라 모델이면 모델
    # 2. 모델이 바뀌어 질때까지 기다려야 하고 모델이 바뀌어 지고 난 다음에 이미지를 생성하도록 api를 구성해주면 될거 같은데
    # 3. 비동기로 하면 안되는게 이건 절대적으로 기다려야 한다. 그렇지 않으면 다른 결과물이 나올 수 있기 떄문임.
    # 4. 이미지가 나왔으면 데이터베이스에다가 저장해두면 좋을거 같긴한데 (데베를 아직 할 줄 모르니까 일단 이건 패스 테스트 환경이니까)
    # 5. 근데 그러면 가능할거 깉은ㄷ[
    def generate_image(self, image_model_id=None, prompt = None, negative_prompt = None):
        
        if image_model_id == None: 
            return None
        
        
        # 긍정, 부정은 공통사항
        # 둘다 None으로 들어오지 않은 경우
        if (prompt is not None) and (negative_prompt is not None):
            self._payload['prompt'] = prompt
            self._payload['negative_prompt'] = negative_prompt
        

        # 이미지 모델에 따라 cfg_scale과 steps 변경
        result = None
        
        # 모델의 옵션 설정
        if image_model_id is not None and image_model_id == "Manmaru":
            self._payload['cfg_scale'] = 11
            self._payload['steps'] = 22
        else:
            # image_model_id 가 None 이거나 또는 image_model_id != ManMaru인 경우
            self._payload['cfg_scale'] = 8.5
            self._payload['steps'] = 30
        
        try:
            response = requests.post(url=f'{self._end_point}/sdapi/v1/txt2img', json=self._payload)
            
            if response.status_code == 200:
                r = response.json()

                for i in r['images']:
                    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

                    png_payload = {
                        "image": "data:image/png;base64," + i
                    }

                    image_info = requests.post(url=f'{self._end_point}/sdapi/v1/png-info', json=png_payload)


                    if image_info.status_code == 200:
                        pnginfo = PngImagePlugin.PngInfo()
                        pnginfo.add_text("parameters", image_info.json().get("info"))
                        # 1~부터 9999까지의 랜덤 정수를 사용해서 저장
                        # 이건 나중에 데이터베이스에다가 저장하는거랑 다르게 하면됨.
                        random_number = random.randrange(1, INF)
                        path = f'{random_number}.png'
                        # @TODO 데이터베이스 연결
                        # 여기서 데이터베이스에 저장을 해야 할거 같다.
                        # 그럼 데이터베이스에 저장해서 저장이 정상적으로 되었다면
                        # 여기서 다시 받은다음에
                        # 그 이미지의 id나 그 이미지를 식별할 수 있는 값을 알려준 다음에
                        # 그걸 서버에서 적용하게 할 순 없으니까
                        # 클라이언트에서 데이터베이스에 통신을 하게 된다면?
                        # 이 api 자체는 이미지를 저장하는 것 뿐
                        # 즉 클라이언트에서 이미지를 생성하고 데이터베이스에 저장해준 뒤
                        # 클라이언트에서 성공적으로 데이터베이스에 저장 되었다는 걸 알려준 다음에
                        # 해당 이미지의 path를 알려주고 그 path나 id를 가지고 쿼리문을 할 수 있도록 하면 어떨까
                        # 그럼 js에서 이미지가 생성 되었다는 걸 알려주고
                        # 그럼 과 동시에 결과에 따라 데이터베이스를 js에서 조회
                        # 조회한 뒤 클라이언트 쪽에서 이미지를 적용.
                        # sqlit를 제공해주니까 이걸 사용해도 좋을거 같네
                        # 테스트니까 이미지 저장용도로만 사용하기에 안성맞춤이고
                        # splite를 써소 해보자
                        image.save(f'{self._save_path}/{random_number}.png', pnginfo=pnginfo)
                        
                        
                        # 이미지 이름을 short int 범위 내에 랜덤하게 생성해서
                        # 이미지 이름을 그렇게 사용하면 어떨까
                        # path를 만들어서 저장하는걸 
                        result = path 
                        
                        
                        return result
                
        except Exception as e:
            return e

        
        
    

    # model 변경
    def change_model(self):
        # 모델을 바꾸는건 성공적으로 되네
        self._option_payload["sd_model_checkpoint"] = self._model
        self._option_payload["sd_lora"] = self._lora
        self._option_payload["sd_vae"] = self._vae
            
        try:
            response = requests.post(url=f'{self._end_point}/sdapi/v1/options', json=self._option_payload)
            
            if response.status_code == 200:
                print("Successful Model Change")
                return response.status_code
            else:
                return "error"
            
        except Exception as e:
            return e

        
        
        
    # 옵션들 보기
    def get_options(self):
        try:
            response = requests.get(url=f'{self._end_point}/sdapi/v1/options')
            print(response.json())
        except Exception as e:
            print(f'Error : {e}')
        
        
    # 모델 이름 가져오기
    def get_model_name(self):
        try:
            response = requests.get(url=f'{self._end_point}/sdapi/v1/sd-models') 
            r = response.json()
            print(r)
        except Exception as e:
            print(e)
            
    # 샘플러 다 보기
    def get_sampler(self):
        response = requests.get(url=f'{self._end_point}/sdapi/v1/samplers')
        r = response.json()
        print(r)
            
    # lora model 가져오기
    def get_LoRa(self):
        response = requests.get(url=f'{self._end_point}/sdapi/v1/loras')
        r = response.json()
        print(r)
        
    # 현재 옵션 상태가져오기
    def get_options(self):
        response = requests.get(url=f'{self._end_point}/sdapi/v1/options')
        r = response.json()
        print(r)
        
    # vae 목록 가져오기
    def get_vae(self):
        response = requests.get(url=f'{self._end_point}/sdapi/v1/sd-vae')
        r = response.json()
        print(r)
        
        
    # def test_image(self):
    #     result = None
    #     self._payload = {
    #         "restore_faces": True,
    #         "prompt": "<lora:brighter-eye1:1>, (1girl), (smile), masterpiece, best quality, high quality",
    #         "negative_prompt": "ugly, lowres, (bad fingers:1.2), (bad anatomy:1.1), bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, nsfw",
    #         "batch_size": 1,
    #         "steps": 22,
    #         "cfg_scale": 11,
    #         "width": 512,
    #         "height": 768,
    #         "sampler_index": "DPM++ 2M"
    #     }
    #     try:
            
    #         response = requests.post(
    #         url=f'{self._end_point}/sdapi/v1/txt2img', json=self._payload)

    #         r = response.json()

    #         for i in r['images']:
    #             image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

    #             png_payload = {
    #                 "image": "data:image/png;base64," + i
    #             }
    #             response2 = requests.post(url=f'{self._end_point}/sdapi/v1/png-info', json=png_payload)

    #             # png 정보를 성공적으로 받아 왔을때만 이미지를 저장한다.
    #             # 이미지를 줄지 아니면 음... 이미지 path를 주는게 가장 현명하지 않을까
    #             # 그 해당 이미지의 path만 찾아서 준다면
    #             # 웹 상에서는 그 이미지 path만 img src로 보여주면 되니까
    #             # 그러면 가능할거 같은데
    #             # 이미지에 랜덤 번호를 부여하는건 어떨까
    #             # 그러면 겹칠일도 없고  
    #             if response2.status_code == 200:
    #                 pnginfo = PngImagePlugin.PngInfo()
    #                 pnginfo.add_text("parameters", response2.json().get("info"))
    #                 # 1~부터 9999까지의 랜덤 정수를 사용해서 저장
    #                 # 이건 나중에 데이터베이스에다가 저장하는거랑 다르게 하면됨.
    #                 random_number = random.randrange(1, 10000)
    #                 result = random_number
    #                 image.save(f'{random_number}.png', pnginfo=pnginfo)

    #             else:
    #                 result = -1
                
    #     except Exception as e:
    #         print(e)

    #     return result
    # # 이미지를 한번씩 초기화 하자
    
    # def test_change_model(self):
    #     # option choice
    #     # manMaru + brighter-eye1, none
    #     # anime + none + orangeMix
    #     # counterfeit + ghibli + clear vae
    #     # counterfeit + chesedays + clear vae
    #     option_payload = {
    #         "sd_model_checkpoint": "manMaru.safetensors [aeb953ac1a]",
    #         "CLIP_stop_at_last_layers": 2,
    #         "sd_lora": "brighter-eye1",
    #         "sd_vae" : "orangemix.vae.pt",
    #     }
    #     # 모델을 바꾸는건 성공적으로 되네
    #     try: 
    #         response = requests.post(url=f'{self._end_point}/sdapi/v1/options', json=option_payload)
    #     except Exception as e:
    #         print(e)
        
    #     # 만약 response 응답 코드가 정상적이라면( 모델이 정상적으로 적용 되었다면 200을 리턴)
    #     if response.status_code == 200:
    #         print(response.status_code)
    #         return response.status_code
    #     # 만약 response 응답 코드가 그 외에 것이라면 (422) 제대로 바뀌지 않았다는 걸 알려줌 
    #     else:
    #         return 422

# stable = StableDiffusionAuto1111()
# stable.get_sampler()
# 테스트하기 위해서
# Ghibli를 선택하기 위해서
# Counterfeit 모델변경
# VAE 적용
# 로라 None
# stable.test_change_model()
# stable.test_image()
# stable.get_model_name()
# stable.get_vae()
# stable.change_model()
# stable.get_LoRa()
# stable.get_options()
