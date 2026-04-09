#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import time
import re

# Ваш API-ключ Dadata
API_KEY = "4e539944b8c5498f253f1664df0ee01e7e0411ad"

def clean_inn(inn_str):
    """Очищает ИНН от мусора и приводит к строковому виду"""
    inn_str = str(inn_str).strip()
    inn_clean = re.sub(r'\D', '', inn_str)
    return inn_clean

def get_company_data(inn):
    """Получение данных компании по ИНН через Dadata"""
    
    url = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party'
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Token {API_KEY}'
    }
    
    data = {
        'query': inn,
        'branch_type': 'MAIN'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            suggestions = result.get('suggestions', [])
            
            if suggestions:
                org = suggestions[0].get('data', {})
                address = org.get('address', {}).get('value', '')
                okved_main = org.get('okved', '')
                okveds_all = org.get('okveds', [])
                okveds_str = ', '.join(okveds_all) if okveds_all else ''
                
                return {
                    'ИНН': inn,
                    'Название_компании': org.get('name', {}).get('short_with_opf', ''),
                    'ОКВЭД_основной': okved_main,
                    'ОКВЭД_все': okveds_str,
                    'Адрес': address,
                    'Статус': org.get('state', {}).get('status', ''),
                    'Тип': org.get('type', ''),
                    'ОГРН': org.get('ogrn', ''),
                    'Руководитель': org.get('management', {}).get('name', '')
                }
            else:
                return {
                    'ИНН': inn,
                    'Название_компании': 'НЕ НАЙДЕНО',
                    'ОКВЭД_основной': 'НЕ НАЙДЕН'
                }
    except Exception as e:
        print(f'Ошибка для ИНН {inn}: {e}')
        return {
            'ИНН': inn,
            'Название_компании': f'ОШИБКА: {e}'
        }

def load_inns_from_file(file_path):
    """Загружает ИНН из текстового файла"""
    inns = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            inn_clean = clean_inn(line)
            if inn_clean and len(inn_clean) >= 10:
                inns.append(inn_clean)
    return inns

# ============ ОСНОВНОЙ СКРИПТ ============

print("=" * 60)
print("Парсер данных компаний по ИНН (Dadata API)")
print("=" * 60)

INPUT_FILE = 'inn.txt'
print(f"\n📂 Загрузка ИНН из файла: {INPUT_FILE}")

try:
    inns = load_inns_from_file(INPUT_FILE)
    print(f"✅ Найдено {len(inns)} уникальных ИНН")
except FileNotFoundError:
    print(f"❌ Файл {INPUT_FILE} не найден!")
    exit(1)

if not inns:
    print("❌ Не удалось загрузить ИНН")
    exit(1)

results = []
total = len(inns)

print(f"\n🚀 Начинаем обработку {total} ИНН...\n")

for i, inn in enumerate(inns, 1):
    print(f"  {i}/{total}: Обработка ИНН {inn}...", end=' ')
    data = get_company_data(inn)
    results.append(data)
    print("✓")
    time.sleep(0.2)

output_file = 'companies.xlsx'
df = pd.DataFrame(results)
df.to_excel(output_file, index=False)

print("\n" + "=" * 60)
print(f"✅ Готово! Обработано {len(results)} из {total} ИНН")
print(f"📁 Результат: {output_file}")
print("=" * 60)
