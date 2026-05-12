#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class WeatherEntry:
    """Модель данных о погоде"""

    def __init__(self, date: str, temperature: float, description: str, precipitation: float):
        self.date = date  # Формат: YYYY-MM-DD
        self.temperature = temperature
        self.description = description
        self.precipitation = precipitation  # в мм
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Конвертация в словарь для JSON"""
        return {
            "date": self.date,
            "temperature": self.temperature,
            "description": self.description,
            "precipitation": self.precipitation,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Создание объекта из словаря"""
        entry = cls(
            data["date"],
            data["temperature"],
            data["description"],
            data["precipitation"]
        )
        entry.created_at = data.get("created_at", datetime.now().isoformat())
        return entry

    def __str__(self) -> str:
        return (f"📅 {self.date} | 🌡️ {self.temperature:+.1f}°C | "
                f"{self.description:12} | 💧 {self.precipitation:.1f} мм")


class WeatherType(ABC):
    """Абстрактный базовый класс для типов погоды (наследование)"""

    @abstractmethod
    def get_emoji(self) -> str:
        pass

    @abstractmethod
    def get_advice(self) -> str:
        pass


class SunnyWeather(WeatherType):
    """Солнечная погода"""

    def get_emoji(self) -> str:
        return "☀️"

    def get_advice(self) -> str:
        return "Наденьте солнцезащитные очки и используйте крем от загара!"


class RainyWeather(WeatherType):
    """Дождливая погода"""

    def get_emoji(self) -> str:
        return "🌧️"

    def get_advice(self) -> str:
        return "Не забудьте взять зонт и одеться теплее!"


class SnowyWeather(WeatherType):
    """Снежная погода"""

    def get_emoji(self) -> str:
        return "❄️"

    def get_advice(self) -> str:
        return "Осторожно на дорогах, наденьте тёплую обувь!"


class CloudyWeather(WeatherType):
    """Облачная погода"""

    def get_emoji(self) -> str:
        return "☁️"

    def get_advice(self) -> str:
        return "Может пойти дождь, лучше взять зонт!"


class WeatherDiary:
    """Основной класс приложения"""

    def __init__(self, data_file: str = "data/weather_data.json"):
        self.data_file = data_file
        self.entries: Dict[str, WeatherEntry] = {}  # Используем словарь для быстрого доступа по дате
        self.load_data()

        # Маппинг описаний погоды к типам
        self.weather_types = {
            "солнечно": SunnyWeather(),
            "дождливо": RainyWeather(),
            "снежно": SnowyWeather(),
            "облачно": CloudyWeather()
        }

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = {
                        date: WeatherEntry.from_dict(entry_data)
                        for date, entry_data in data.items()
                    }
                print(f"✅ Загружено {len(self.entries)} записей о погоде")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки данных: {e}")
                self.entries = {}
        else:
            print("📭 Файл данных не найден, создан новый")
            self.entries = {}

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

            data = {
                date: entry.to_dict()
                for date, entry in self.entries.items()
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"⚠️ Ошибка сохранения данных: {e}")
            return False

    def validate_date(self, date_str: str) -> Optional[str]:
        """Проверка корректности даты"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("❌ Ошибка: Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return None

    def validate_temperature(self, temp_str: str) -> Optional[float]:
        """Проверка корректности температуры"""
        try:
            temp = float(temp_str)
            if temp < -50 or temp > 50:
                print("❌ Ошибка: Температура должна быть в диапазоне от -50°C до +50°C")
                return None
            return round(temp, 1)
        except ValueError:
            print("❌ Ошибка: Введите корректное число для температуры!")
            return None

    def validate_precipitation(self, precip_str: str) -> Optional[float]:
        """Проверка корректности осадков"""
        try:
            precip = float(precip_str)
            if precip < 0:
                print("❌ Ошибка: Осадки не могут быть отрицательными!")
                return None
            if precip > 500:
                print("❌ Ошибка: Слишком большое значение осадков!")
                return None
            return round(precip, 1)
        except ValueError:
            print("❌ Ошибка: Введите корректное число для осадков!")
            return None

    def add_entry(self, date: str, temperature: float, description: str, precipitation: float):
        """Добавление новой записи о погоде"""
        if date in self.entries:
            print(f"⚠️ Запись за {date} уже существует! Используйте редактирование.")
            return False

        entry = WeatherEntry(date, temperature, description, precipitation)
        self.entries[date] = entry

        if self.save_data():
            # Показываем совет в зависимости от погоды
            weather_type = self.weather_types.get(description.lower())
            if weather_type:
                print(f"{weather_type.get_emoji()} {weather_type.get_advice()}")

            print(f"✅ Запись о погоде за {date} успешно добавлена!")
            return True
        return False

    def view_all(self):
        """Просмотр всех записей"""
        if not self.entries:
            print("\n📭 Нет записей о погоде.")
            return

        print("\n" + "="*70)
        print("📊 ВСЕ ЗАПИСИ О ПОГОДЕ")
        print("="*70)

        sorted_dates = sorted(self.entries.keys())

        for date in sorted_dates:
            entry = self.entries[date]
            print(entry)

        # Статистика
        temps = [e.temperature for e in self.entries.values()]
        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        min_temp = min(temps)

        print("="*70)
        print(f"📈 Статистика:")
        print(f"   Средняя температура: {avg_temp:+.1f}°C")
        print(f"   Максимальная температура: {max_temp:+.1f}°C")
        print(f"   Минимальная температура: {min_temp:+.1f}°C")
        print(f"   Количество записей: {len(self.entries)}")

    def delete_entry(self, date: str) -> bool:
        """Удаление записи по дате"""
        if date in self.entries:
            del self.entries[date]
            if self.save_data():
                print(f"🗑️ Запись за {date} удалена")
                return True
        else:
            print(f"❌ Запись за {date} не найдена!")
        return False

    def filter_by_date_range(self, start_date: str, end_date: str):
        """Фильтрация по диапазону дат"""
        filtered = {
            date: entry for date, entry in self.entries.items()
            if start_date <= date <= end_date
        }

        self.display_filtered_results(filtered, f"периоду {start_date} - {end_date}")
        return filtered

    def filter_by_temperature(self, min_temp: float, max_temp: float):
        """Фильтрация по диапазону температур"""
        filtered = {
            date: entry for date, entry in self.entries.items()
            if min_temp <= entry.temperature <= max_temp
        }

        self.display_filtered_results(filtered, f"температуре от {min_temp}°C до {max_temp}°C")
        return filtered

    def display_filtered_results(self, filtered: Dict, filter_desc: str):
        """Отображение отфильтрованных результатов"""
        if not filtered:
            print(f"\n❌ Не найдено записей по {filter_desc}.")
            return

        print(f"\n🔍 Результаты фильтрации по {filter_desc}:")
        print("-"*60)

        for date in sorted(filtered.keys()):
            print(filtered[date])

        # Статистика по отфильтрованным данным
        temps = [e.temperature for e in filtered.values()]
        avg_temp = sum(temps) / len(temps)

        print("-"*60)
        print(f"📊 Средняя температура: {avg_temp:+.1f}°C")
        print(f"📊 Количество записей: {len(filtered)}")

    def plot_temperature_graph(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None):
        """Построение графика температуры"""
        if not self.entries:
            print("\n❌ Нет данных для построения графика!")
            return

        # Фильтрация данных если указаны даты
        if start_date and end_date:
            filtered = {
                date: entry for date, entry in self.entries.items()
                if start_date <= date <= end_date
            }
        else:
            filtered = self.entries

        if not filtered:
            print("\n❌ Нет данных за указанный период!")
            return

        # Подготовка данных
        sorted_dates = sorted(filtered.keys())
        dates = [datetime.strptime(date, "%Y-%m-%d") for date in sorted_dates]
        temperatures = [filtered[date].temperature for date in sorted_dates]

        # Создание графика
        plt.figure(figsize=(12, 6))
        plt.plot(dates, temperatures, marker='o', linewidth=2, markersize=6,
                color='#3498db', label='Температура')

        # Настройка графика
        plt.title('График температуры по дням', fontsize=16, fontweight='bold')
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Температура (°C)', fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend()

        # Настройка оси X
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gcf().autofmt_xdate()  # Поворот подписей для читаемости

        # Добавление горизонтальной линии на 0°C
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Ноль градусов')

        # Добавление аннотаций с максимальной и минимальной температурой
        max_temp_idx = temperatures.index(max(temperatures))
        min_temp_idx = temperatures.index(min(temperatures))

        plt.annotate(f'Макс: {temperatures[max_temp_idx]:+.1f}°C',
                    xy=(dates[max_temp_idx], temperatures[max_temp_idx]),
                    xytext=(10, 10), textcoords='offset points',
                    arrowprops=dict(arrowstyle='->', color='green'))

        plt.annotate(f'Мин: {temperatures[min_temp_idx]:+.1f}°C',
                    xy=(dates[min_temp_idx], temperatures[min_temp_idx]),
                    xytext=(10, -15), textcoords='offset points',
                    arrowprops=dict(arrowstyle='->', color='red'))

        # Заполнение области под графиком
        plt.fill_between(dates, temperatures, alpha=0.2, color='#3498db')

        # Показ статистики на графике
        avg_temp = sum(temperatures) / len(temperatures)
        plt.text(0.02, 0.95, f'Средняя: {avg_temp:+.1f}°C',
                transform=plt.gca().transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        plt.show()

    def get_statistics(self):
        """Получение расширенной статистики"""
        if not self.entries:
            print("\n📭 Нет данных для статистики")
            return

        temps = [e.temperature for e in self.entries.values()]
        precipitations = [e.precipitation for e in self.entries.values()]

        print("\n" + "="*50)
        print("📊 РАСШИРЕННАЯ СТАТИСТИКА")
        print("="*50)
        print(f"Количество записей: {len(self.entries)}")
        print(f"\n🌡️ Температура:")
        print(f"   Средняя: {sum(temps)/len(temps):+.1f}°C")
        print(f"   Максимальная: {max(temps):+.1f}°C")
        print(f"   Минимальная: {min(temps):+.1f}°C")
        print(f"   Размах: {max(temps)-min(temps):.1f}°C")

        print(f"\n💧 Осадки:")
        print(f"   Средние: {sum(precipitations)/len(precipitations):.1f} мм")
        print(f"   Максимальные: {max(precipitations):.1f} мм")
        print(f"   Минимальные: {min(precipitations):.1f} мм")

        # Анализ погоды
        descriptions = [e.description.lower() for e in self.entries.values()]
        from collections import Counter
        weather_counts = Counter(descriptions)

        print(f"\n☁️ Типы погоды:")
        for weather, count in weather_counts.most_common():
            percentage = (count / len(self.entries)) * 100
            print(f"   {weather}: {count} раз ({percentage:.1f}%)")


class ConsoleUI:
    """Консольный интерфейс пользователя"""

    def __init__(self):
        self.diary = WeatherDiary()

    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_menu(self):
        """Вывод главного меню"""
        print("\n" + "="*50)
        print("🌤️ WEATHER DIARY - Дневник погоды")
        print("="*50)
        print("1. ➕ Добавить запись о погоде")
        print("2. 👁️ Просмотреть все записи")
        print("3. 🗑️ Удалить запись")
        print("4. 🔍 Фильтрация записей")
        print("5. 📈 Построить график температуры")
        print("6. 📊 Статистика и анализ")
        print("0. 🚪 Выход")
        print("-"*50)

    def filter_menu(self):
        """Меню фильтрации"""
        print("\n🔍 ФИЛЬТРАЦИЯ ЗАПИСЕЙ")
        print("-"*30)
        print("1. По диапазону дат")
        print("2. По диапазону температур")
        print("0. Назад")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            print("\nВведите диапазон дат (формат: ГГГГ-ММ-ДД):")
            start = input("Начальная дата: ").strip()
            end = input("Конечная дата: ").strip()

            if self.diary.validate_date(start) and self.diary.validate_date(end):
                self.diary.filter_by_date_range(start, end)

        elif choice == "2":
            try:
                min_temp = float(input("Минимальная температура (°C): ").strip())
                max_temp = float(input("Максимальная температура (°C): ").strip())

                if min_temp > max_temp:
                    print("❌ Минимальная температура не может быть больше максимальной!")
                    return

                self.diary.filter_by_temperature(min_temp, max_temp)
            except ValueError:
                print("❌ Введите корректные числа!")

    def add_entry_ui(self):
        """UI для добавления записи"""
        print("\n➕ ДОБАВЛЕНИЕ ЗАПИСИ О ПОГОДЕ")
        print("-"*40)

        # Ввод даты
        while True:
            date = input("📅 Дата (ГГГГ-ММ-ДД): ").strip()
            valid_date = self.diary.validate_date(date)
            if valid_date:
                if date in self.diary.entries:
                    print(f"⚠️ Запись за {date} уже существует!")
                    edit = input("Хотите отредактировать существующую запись? (д/н): ").strip().lower()
                    if edit == 'д':
                        self.edit_entry_ui(date)
                    return
                break

        # Ввод температуры
        while True:
            temp_str = input("🌡️ Температура (°C): ").strip()
            temp = self.diary.validate_temperature(temp_str)
            if temp is not None:
                break

        # Ввод описания погоды
        print("\n☁️ Типы погоды:")
        weather_types = ["солнечно", "облачно", "дождливо", "снежно"]
        for i, wtype in enumerate(weather_types, 1):
            print(f"   {i}. {wtype}")

        while True:
            choice = input("\nВыберите тип погоды (1-4): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(weather_types):
                description = weather_types[int(choice)-1]
                break
            else:
                description = input("Или введите своё описание: ").strip()
                if description:
                    break
                print("❌ Введите корректное описание!")

        # Ввод осадков
        while True:
            precip_str = input("💧 Осадки (мм): ").strip()
            precip = self.diary.validate_precipitation(precip_str)
            if precip is not None:
                break

        self.diary.add_entry(date, temp, description, precip)

    def edit_entry_ui(self, date: str):
        """Редактирование существующей записи"""
        print(f"\n✏️ РЕДАКТИРОВАНИЕ ЗАПИСИ ЗА {date}")
        print("-"*40)

        current = self.diary.entries[date]
        print(f"Текущие данные: {current}")

        # Редактирование температуры
        new_temp = input(f"Новая температура (Enter - {current.temperature}°C): ").strip()
        if new_temp:
            temp = self.diary.validate_temperature(new_temp)
            if temp is not None:
                current.temperature = temp

        # Редактирование описания
        print("\nТипы погоды: солнечно, облачно, дождливо, снежно")
        new_desc = input(f"Новое описание (Enter - {current.description}): ").strip()
        if new_desc:
            current.description = new_desc

        # Редактирование осадков
        new_precip = input(f"Новые осадки (Enter - {current.precipitation} мм): ").strip()
        if new_precip:
            precip = self.diary.validate_precipitation(new_precip)
            if precip is not None:
                current.precipitation = precip

        self.diary.save_data()
        print("✅ Запись обновлена!")

    def delete_entry_ui(self):
        """UI для удаления записи"""
        if not self.diary.entries:
            print("\n📭 Нет записей для удаления")
            return

        self.diary.view_all()
        date = input("\nВведите дату для удаления (ГГГГ-ММ-ДД): ").strip()

        if self.diary.validate_date(date):
            self.diary.delete_entry(date)

    def plot_graph_ui(self):
        """UI для построения графика"""
        if not self.diary.entries:
            print("\n📭 Нет данных для построения графика")
            return

        print("\n📈 ПОСТРОЕНИЕ ГРАФИКА ТЕМПЕРАТУРЫ")
        print("-"*40)
        print("1. За весь период")
        print("2. За выбранный период")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            self.diary.plot_temperature_graph()
        elif choice == "2":
            start = input("Начальная дата (ГГГГ-ММ-ДД): ").strip()
            end = input("Конечная дата (ГГГГ-ММ-ДД): ").strip()

            if self.diary.validate_date(start) and self.diary.validate_date(end):
                self.diary.plot_temperature_graph(start, end)

    def run(self):
        """Запуск приложения"""
        while True:
            self.print_menu()
            choice = input("Ваш выбор: ").strip()

            if choice == "1":
                self.add_entry_ui()
            elif choice == "2":
                self.diary.view_all()
            elif choice == "3":
                self.delete_entry_ui()
            elif choice == "4":
                self.filter_menu()
            elif choice == "5":
                self.plot_graph_ui()
            elif choice == "6":
                self.diary.get_statistics()
            elif choice == "0":
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")

            input("\nНажмите Enter для продолжения...")
            self.clear_screen()


def main():
    """Точка входа"""
    try:
        app = ConsoleUI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n⚠️ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
