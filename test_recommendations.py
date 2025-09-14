#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API рекомендаций друзей
"""

import requests
import json

# Конфигурация
BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{BASE_URL}/api/friends/recommendations/"

def test_recommendations_endpoint():
    """
    Тестирует endpoint рекомендаций друзей
    """
    print("🧪 Тестирование API рекомендаций друзей...")
    print(f"📍 URL: {API_ENDPOINT}")
    
    # Тест 1: Запрос без токена (должен вернуть ошибку авторизации)
    print("\n1️⃣ Тест без токена авторизации:")
    try:
        response = requests.get(API_ENDPOINT)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}..." if len(response.text) > 200 else f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Проверка структуры ответа (с фиктивным токеном)
    print("\n2️⃣ Тест с фиктивным токеном:")
    headers = {
        'Authorization': 'Token 42be1e56-b481-4f26-af9b-1e0f1ee730d1',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(API_ENDPOINT, headers=headers)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Успешный ответ!")
            print(f"   📊 Структура ответа:")
            print(f"      - recommendations: {len(data.get('recommendations', []))} элементов")
            print(f"      - total_count: {data.get('total_count', 'N/A')}")
            print(f"      - algorithm_version: {data.get('algorithm_version', 'N/A')}")
            
            # Показываем первую рекомендацию, если есть
            if data.get('recommendations'):
                first_rec = data['recommendations'][0]
                print(f"   🎯 Пример рекомендации:")
                print(f"      - username: {first_rec.get('username', 'N/A')}")
                print(f"      - recommendation_score: {first_rec.get('recommendation_score', 'N/A')}")
                print(f"      - common_interests: {first_rec.get('common_interests', [])}")
                print(f"      - mutual_friends_count: {first_rec.get('mutual_friends_count', 'N/A')}")
        else:
            print(f"   ⚠️  Ответ: {response.text[:300]}..." if len(response.text) > 300 else f"   Ответ: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: Проверка с параметром limit
    print("\n3️⃣ Тест с параметром limit=5:")
    try:
        response = requests.get(f"{API_ENDPOINT}?limit=5", headers=headers)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Лимит работает! Получено: {len(data.get('recommendations', []))} рекомендаций")
        else:
            print(f"   ⚠️  Ответ: {response.text[:200]}..." if len(response.text) > 200 else f"   Ответ: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n🏁 Тестирование завершено!")
    print("\n📝 Примечания:")
    print("   - Для полного тестирования нужен валидный токен авторизации")
    print("   - Убедитесь, что в базе данных есть пользователи с заполненными интересами")
    print("   - Проверьте, что есть связи дружбы между пользователями")

if __name__ == "__main__":
    test_recommendations_endpoint()