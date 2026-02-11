#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アニメキャラクター情報カード生成スクリプト
著作権に配慮したテキストベースの画像
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import random
import boto3
from io import BytesIO


def generate_character_info_card():
    """
    キャラクター情報カード画像を生成（テキストのみ、著作権配慮）
    """
    print("🎨 キャラクター情報カード生成中...")
    
    width = 1200
    height = 800
    
    # グラデーション背景
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # 宇宙風の背景グラデーション
    for y in range(height):
        r = int(10 + (50 * y / height))
        g = int(20 + (80 * y / height))
        b = int(80 + (175 * y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 星を追加
    for i in range(150):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 4)
        brightness = random.randint(200, 255)
        draw.ellipse([x, y, x+size, y+size], fill=(brightness, brightness, brightness))
    
    # カード枠
    card_margin = 100
    draw.rectangle(
        [card_margin, card_margin, width-card_margin, height-card_margin],
        outline=(255, 215, 0),
        width=5
    )
    
    # 半透明の背景
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [card_margin+10, card_margin+10, width-card_margin-10, height-card_margin-10],
        fill=(0, 0, 0, 180)
    )
    image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(image)
    
    # キャラクター情報（著作権に配慮したテキストのみ）
    text_x = card_margin + 50
    text_y = card_margin + 50
    line_height = 60
    
    info_texts = [
        "CHARACTER DATA CARD",
        "",
        "Name: Camille Vidan",
        "Series: Mobile Suit Z Gundam",
        "Role: Pilot",
        "Notable: AEUG Member",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "※ This is a text-based information card",
        "※ No copyrighted images are used"
    ]
    
    for i, text in enumerate(info_texts):
        if i == 0:
            # タイトルは大きく
            y_pos = text_y + (i * line_height)
            draw.text((text_x, y_pos), text, fill=(255, 215, 0))
        elif text.startswith("※"):
            # 注釈は小さく
            y_pos = text_y + (i * line_height)
            draw.text((text_x, y_pos), text, fill=(150, 150, 150))
        else:
            y_pos = text_y + (i * line_height)
            draw.text((text_x, y_pos), text, fill=(255, 255, 255))
    
    # 装飾的な要素（抽象的な図形）
    for i in range(5):
        x = random.randint(width-300, width-150)
        y = random.randint(150, height-150)
        size = random.randint(30, 80)
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(200, 255)
        )
        draw.ellipse([x, y, x+size, y+size], outline=color, width=2)
    
    print("✅ キャラクター情報カード生成完了")
    return image


def generate_abstract_mecha_art():
    """
    抽象的なメカアート（著作権フリー）
    """
    print("🎨 抽象メカアート生成中...")
    
    width = 1200
    height = 800
    
    # 背景
    image = Image.new('RGB', (width, height), (20, 20, 40))
    draw = ImageDraw.Draw(image)
    
    # 宇宙背景
    for i in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 3)
        draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255))
    
    # 抽象的なメカっぽい図形
    colors = [
        (200, 50, 50),    # 赤
        (50, 150, 255),   # 青
        (255, 215, 0),    # 金
        (150, 150, 150)   # グレー
    ]
    
    center_x, center_y = width//2, height//2
    
    # 中心の大きな円（コックピット風）
    draw.ellipse(
        [center_x-100, center_y-100, center_x+100, center_y+100],
        outline=(255, 215, 0),
        width=5
    )
    
    # 周囲の装飾（パーツ風）
    for i in range(8):
        angle = (360 / 8) * i
        import math
        rad = math.radians(angle)
        x = center_x + int(200 * math.cos(rad))
        y = center_y + int(200 * math.sin(rad))
        
        color = random.choice(colors)
        size = random.randint(30, 60)
        draw.rectangle(
            [x-size//2, y-size//2, x+size//2, y+size//2],
            outline=color,
            width=3
        )
    
    # テキスト
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((40, 40), "ABSTRACT MECHA ART", fill=(255, 215, 0))
    draw.text((40, 80), f"Generated: {timestamp}", fill=(200, 200, 200))
    
    print("✅ 抽象メカアート生成完了")
    return image


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
    filename = f"character-cards/{now.strftime('%Y/%m/%d/%H%M%S')}.png"
    
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
    print("=" * 50)
    print("🚀 画像生成プログラム開始")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # ランダムに画像タイプを選択
        image_type = random.choice(['info_card', 'abstract_mecha'])
        
        if image_type == 'info_card':
            image = generate_character_info_card()
        else:
            image = generate_abstract_mecha_art()
        
        filename = upload_to_cloudflare_r2(image)
        
        print("=" * 50)
        print("✨ すべての処理が完了しました！")
        print(f"📷 保存ファイル: {filename}")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print(f"❌ エラーが発生しました: {e}")
        print("=" * 50)
        raise


if __name__ == "__main__":
    main()
