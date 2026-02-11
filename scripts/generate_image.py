#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hugging Face APIを使用して実写風画像を生成
新しいエンドポイント（router.huggingface.co）に対応
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw
import boto3
from io import BytesIO
import requests
import random
import time


def generate_realistic_character_image():
    """
    Hugging Face APIを使用して実写風キャラクター画像を生成
    """
    print("🎨 AI画像生成中（Hugging Face API使用）...")
    
    api_token = os.getenv('HUGGINGFACE_API_TOKEN')
    if not api_token:
        raise ValueError("❌ HUGGINGFACE_API_TOKEN が設定されていません")
    
    # 新しいエンドポイントに変更
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
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": selected_prompt,
        "parameters": {
            "negative_prompt": "ugly, blurry, low quality, distorted, deformed",
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    }
    
    # API呼び出し（リトライ機能付き）
    max_retries = 3
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            print(f"⏳ API呼び出し中... (試行 {attempt + 1}/{max_retries})")
            response = requests.post(api_url, headers=headers, json=payload, timeout=180)
            
            if response.status_code == 200:
                # 成功：画像を取得
                image = Image.open(BytesIO(response.content))
                print("✅ 画像生成完了")
                return image
                
            elif response.status_code == 503:
                # モデルがロード中
                print(f"⏳ モデルロード中... {retry_delay}秒待機")
                time.sleep(retry_delay)
                retry_delay *= 2  # 待機時間を倍にする
                continue
                
            else:
                # その他のエラー
                error_msg = response.text
                print(f"❌ API Error: {response.status_code} - {error_msg}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ {retry_delay}秒後に再試行...")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"API Error: {response.status_code} - {error_msg}")
                    
        except requests.exceptions.Timeout:
            print(f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"⏳ {retry_delay}秒後に再試行...")
                time.sleep(retry_delay)
                continue
            else:
                raise Exception("API呼び出しがタイムアウトしました")
    
    raise Exception("画像生成に失敗しました")


def generate_fallback_image():
    """
    フォールバック：シンプルな画像を生成（API失敗時用）
    """
    print("🎨 フォールバック画像を生成中...")
    
    width = 1200
    height = 800
    
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # グラデーション背景
    for y in range(height):
        r = int(20 + (80 * y / height))
        g = int(40 + (120 * y / height))
        b = int(100 + (155 * y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 装飾的な円
    for i in range(20):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(30, 150)
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(150, 255)
        )
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    
    # テキスト
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 背景ボックス
    draw.rectangle([30, 30, 600, 150], fill=(0, 0, 0, 200))
    
    # テキスト描画
    draw.text((50, 50), "AI Image Generation", fill=(255, 255, 255))
    draw.text((50, 90), f"Generated: {timestamp}", fill=(200, 200, 200))
    
    print("✅ フォールバック画像生成完了")
    return image


def add_watermark(image):
    """
    画像にタイムスタンプと情報を追加
    """
    img_with_text = image.copy()
    draw = ImageDraw.Draw(img_with_text)
    
    width, height = img_with_text.size
    
    # タイムスタンプ
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 半透明の背景（左上）
    draw.rectangle([10, 10, 450, 80], fill=(0, 0, 0, 200))
    
    # テキスト
    draw.text((20, 20), f"Generated: {timestamp}", fill=(255, 255, 255))
    draw.text((20, 50), "AI Generated Image", fill=(200, 200, 200))
    
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
        # まずAI画像生成を試みる
        try:
            image = generate_realistic_character_image()
        except Exception as ai_error:
            print(f"⚠️  AI生成失敗: {ai_error}")
            print("📦 フォールバック画像を使用します")
            image = generate_fallback_image()
        
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
        print("=" * 60)
        raise


if __name__ == "__main__":
    main()
