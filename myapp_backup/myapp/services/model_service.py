# import torch
# import numpy as np
# from transformers import AutoTokenizer, AutoModelForCausalLM

# class MedicalChatModel:
#     def __init__(self):
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.dtype = torch.bfloat16
#         self.model_name = "/data/esh/myapp/3dmodel/M3D-LaMed-Phi-3-4B"
#         self.proj_out_num = 256

#         self.tokenizer = AutoTokenizer.from_pretrained(
#             self.model_name,
#             model_max_length=512,
#             padding_side="right",
#             use_fast=False,
#             trust_remote_code=True
#         )

#         self.model = AutoModelForCausalLM.from_pretrained(
#             self.model_name,
#             torch_dtype=self.dtype,
#             device_map="auto",
#             trust_remote_code=True
#         )

#     def infer(self, image_path, question):
#         image_np = np.load("/data/esh/myapp/example_00.npy")
#         image_pt = torch.from_numpy(image_np).unsqueeze(0).to(
#             dtype=self.dtype, device=self.device
#         )

#         image_tokens = "<im_patch>" * self.proj_out_num
#         input_txt = image_tokens + question
#         input_ids = self.tokenizer(input_txt, return_tensors="pt")["input_ids"].to(self.device)


#         with torch.no_grad():
#             generation, seg_logit = self.model.generate(
#                 image_pt,
#                 input_ids,
#                 seg_enable=True,
#                 max_new_tokens=256,
#                 do_sample=True,
#                 top_p=0.9,
#                 temperature=1.0
#             )

#         text = self.tokenizer.batch_decode(generation, skip_special_tokens=True)[0]
#         seg_mask = (torch.sigmoid(seg_logit) > 0.5).float()

#         return text, seg_mask.cpu().numpy()[0]

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Optional


class MedicalChatModel:
    """
    医学多模态对话模型服务（单例）
    """

    def __init__(
        self,
        model_name: str,
        device: Optional[str] = None,
        dtype: torch.dtype = torch.bfloat16,
        proj_out_num: int = 256
    ):
        self.device = (
            torch.device(device)
            if device
            else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.dtype = dtype
        self.model_name = model_name
        self.proj_out_num = proj_out_num

        self._load_model()

    def _load_model(self):
        """模型与 tokenizer 初始化（仅一次）"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            model_max_length=1024,
            padding_side="right",
            use_fast=False,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=self.dtype,
            device_map="auto",
            trust_remote_code=True
        )

        self.model.eval()

    # =========================
    # 多模态推理接口
    # =========================
    def infer(
        self,
        npy_path: str,
        question: str,
        chat_history: Optional[List[Dict]] = None,
        max_new_tokens: int = 256
    ):
        """
        参数:
            npy_path: npy 文件路径
            question: 当前用户问题
            chat_history: [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        """

        # ---------- 加载影像 ----------
        image_np = np.load(npy_path)
        image_pt = torch.from_numpy(image_np).unsqueeze(0).to(
            dtype=self.dtype, device=self.device
        )

        # ---------- 构造对话上下文 ----------
        prompt = self._build_prompt(question, chat_history)

        input_ids = self.tokenizer(
            prompt,
            return_tensors="pt"
        )["input_ids"].to(self.device)

        # ---------- 模型推理 ----------
        with torch.no_grad():
            generation, seg_logit = self.model.generate(
                image_pt,
                input_ids,
                seg_enable=True,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_p=0.9,
                temperature=1.0
            )

        # ---------- 解析输出 ----------
        answer_text = self.tokenizer.batch_decode(
            generation,
            skip_special_tokens=True
        )[0]

        seg_mask = None
        if seg_logit is not None:
            seg_mask = (
                torch.sigmoid(seg_logit) > 0.5
            ).float().cpu().numpy()[0]

        return {
            "answer": answer_text,
            "segmentation": seg_mask
        }

    # =========================
    # Prompt 构造
    # =========================
    def _build_prompt(
        self,
        question: str,
        chat_history: Optional[List[Dict]]
    ) -> str:
        """
        构造符合多模态模型的 prompt
        """
        image_tokens = "<im_patch>" * self.proj_out_num

        prompt_parts = [image_tokens]

        if chat_history:
            for msg in chat_history:
                role = msg["role"]
                content = msg["content"]
                prompt_parts.append(f"{role}: {content}")

        prompt_parts.append(f"user: {question}")
        prompt_parts.append("assistant:")

        return "\n".join(prompt_parts)
