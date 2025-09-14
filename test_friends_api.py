#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API друзей с полной информацией о пользователях
"""

import requests
import json

# Конфигурация
BASE_URL = "http://127.0.0.1:8000"
FRIENDS_ENDPOINT = f"{BASE_URL}/api/friends/"

def test_friends_endpoint():
    """
    Тестирует endpoint списка друзей с новым форматом
    """
    print("🧪 Тестирование API списка друзей...")
    print(f"📍 URL: {FRIENDS_ENDPOINT}")
    
    # Тест 1: Запрос без токена (должен вернуть ошибку авторизации)
    print("\n1️⃣ Тест без токена авторизации:")
    try:
        response = requests.get(FRIENDS_ENDPOINT)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}..." if len(response.text) > 200 else f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Проверка структуры ответа (с фиктивным токеном)
    print("\n2️⃣ Тест с фиктивным токеном:")
    headers = {
        'Authorization': 'Bearer fake_token_for_testing',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(FRIENDS_ENDPOINT, headers=headers)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Успешный ответ!")
            print(f"   📊 Количество записей: {len(data)}")
            
            # Показываем первую запись, если есть
            if data:
                first_friendship = data[0]
                print(f"   🎯 Пример записи дружбы:")
                print(f"      - status: {first_friendship.get('status', 'N/A')}")
                print(f"      - created_at: {first_friendship.get('created_at', 'N/A')}")
                
                # Проверяем структуру from_user
                from_user = first_friendship.get('from_user', {})
                if isinstance(from_user, dict):
                    print(f"      - from_user:")
                    print(f"        * id: {from_user.get('id', 'N/A')}")
                    print(f"        * username: {from_user.get('username', 'N/A')}")
                    print(f"        * full_name: {from_user.get('full_name', 'N/A')}")
                    print(f"        * level: {from_user.get('level', 'N/A')}")
                    print(f"        * avatar_url: {from_user.get('avatar_url', 'N/A')}")
                    print(f"        * bio: {from_user.get('bio', 'N/A')[:50]}..." if from_user.get('bio') else "        * bio: N/A")
                else:
                    print(f"      - from_user: {from_user} (старый формат - только ID)")
                
                # Проверяем структуру to_user
                to_user = first_friendship.get('to_user', {})
                if isinstance(to_user, dict):
                    print(f"      - to_user:")
                    print(f"        * id: {to_user.get('id', 'N/A')}")
                    print(f"        * username: {to_user.get('username', 'N/A')}")
                    print(f"        * full_name: {to_user.get('full_name', 'N/A')}")
                    print(f"        * level: {to_user.get('level', 'N/A')}")
                else:
                    print(f"      - to_user: {to_user} (старый формат - только ID)")
            else:
                print(f"   📝 Список друзей пуст")
        else:
            print(f"   ⚠️  Ответ: {response.text[:300]}..." if len(response.text) > 300 else f"   Ответ: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n🏁 Тестирование завершено!")
    print("\n📝 Ожидаемый новый формат:")
    print("   - from_user и to_user теперь содержат полную информацию о пользователях")
    print("   - Включает: id, username, full_name, avatar_url, bio, level, interests, created_at")
    print("   - Исключает: токен и другие чувствительные данные")

if __name__ == "__main__":
    test_friends_endpoint()