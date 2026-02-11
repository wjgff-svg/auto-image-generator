#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hugging Face APIを使用して実写風画像を生成
Stable Diffusionモデルを利用
"""

import os
from datetime import datetime
from PIL import Image
import boto3
from io import BytesIO
import requests
import random


def generate_realistic_character_image():
    """
    Hugging Face APIを使用して実写風キャラクター画像を生成
    """
    print("🎨 AI画像生成中（Hugging Face API使用）...")
    
    api_token = os.getenv('HUGGINGFACE_API_TOKEN')
    if not api_token:
        raise ValueError("❌ HUGGINGFACE_API_TOKEN が設定されていません")
    
    # 使用するモデル（無料で使える実写系モデル）
    model_id = "stabilityai/stable-diffusion-2-1"
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    # プロンプトのバリエーション
    prompts = [
        "realistic photo of a young japanese man with brown short hair, pilot uniform, anime character inspired, studio lighting, high quality, 4k",
        "photo realistic portrait of a young male pilot, short brown hair, serious expression, military uniform, cinematic lighting",
        "professional photo, young asian male pilot, brown hair, confident look, aviation uniform, detailed face, 8k quality",
        "realistic photograph, handsome young man in pilot suit, short brown hair, determined eyes, military aviation, studio portrait"
    ]
    
    selected_prompt = random.choice(prompts)
    print(f"📝 プロンプト: {selected_prompt}")
    
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    payload = {
        "inputs": selected_prompt,
        "parameters": {
            "negative_prompt": "ugly, blurry, low quality, distorted, anime, cartoon",
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        }
    }
    
    # API呼び出し
    print("⏳ API呼び出し中...")
    response = requests.post(api_url, headers=headers, json=payload, timeout=120)
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    # 画像を取得
    image = Image.open(BytesIO(response.content))
    print("✅ 画像生成完了")
    
    return image


def add_watermark(image):
    """
    画像にタイムスタンプと情報を追加
    """
    from PIL import ImageDraw
    
    img_with_text = image.copy()
    draw = ImageDraw.Draw(img_with_text)
    
    width, height = img_with_text.size
    
    # タイムスタンプ
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 半透明の背景
    draw.rectangle([10, 10, 450, 80], fill=(0, 0, 0, 200))
    
    # テキスト
    draw.text((20, 20), f"Generated: {timestamp}", fill=(255, 255, 255))
    draw.text((20, 50), "AI Generated Image (Stable Diffusion)", fill=(200, 200, 200))
    
    return img_with_text


def upload_to_cloudflare_r2(image):
    """Cloudflare R2に画像をアップロード"""
    print("☁️  Cloudflare R2にアップロード中...")
    
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('R2_BUCKET_NAME')
    
    if not all([account_id, access_key, secret_key, bucket_name]):
        raise ValueError("❌ R2の設定が不足しています")
    
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto'
    )
    
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG', optimize=True)
    img_byte_arr.seek(0)
    
    now = datetime.now()
    filename = f"ai-generated/{now.strftime('%Y/%m/%d/%H%M%S')}.png"
    
    try:
        s3_client.upload_fileobj(
            img_byte_arr,
            bucket_name,
            filename,
            ExtraArgs={'ContentType': 'image/png'}
        )
        print(f"✅ アップロード成功: {filename}")
        return filename
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        raise


def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 AI画像生成プログラム開始")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # AI画像生成
        image = generate_realistic_character_image()
        
        # 透かしを追加
        image_with_watermark = add_watermark(image)
        
        # アップロード
        filename = upload_to_cloudflare_r2(image_with_watermark)
        
        print("=" * 60)
        print("✨ すべての処理が完了しました！")
        print(f"📷 保存ファイル: {filename}")
        print("=" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"❌ エラーが発生しました: {e}")
        print("🔧 対処方法:")
        print("1. HUGGINGFACE_API_TOKEN が正しく設定されているか確認")
        print("2. Hugging Face APIの利用制限を確認")
        print("3. インターネット接続を確認")
        print("=" * 60)
        raise


if __name__ == "__main__":
    main()
