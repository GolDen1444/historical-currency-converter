import os
import json
import requests
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    print("Ошибка: API_KEY не найден в файле .env")
    print("Создайте файл .env с содержимым: API_KEY=ваш_ключ")
    API_KEY = "demo"

# ==================== ОСНОВНОЙ КЛАСС КОНВЕРТЕРА ====================
class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("💱 Универсальный конвертер валют")
        self.root.geometry("750x750")
        self.root.resizable(False, False)
        
        # Центрирование окна
        self.center_window()
        
        # Инициализация данных
        self.api_data = None
        self.api_data_eur = None
        
        
        self.historical_rates = {
            "USSR RUB": 135.5,        # 1 USSR RUB = 135.5 RUS RUB
            "RUS EMPIRE RUB": 1200,   # 1 RUS EMPIRE RUB = 1200 RUS RUB
        }
        
        # Загрузка курсов из API
        self.load_exchange_rates()
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Загрузка сохраненных настроек
        self.load_settings()
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = 750
        height = 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_exchange_rates(self):
        """Загрузка курсов валют из API в отдельном потоке"""
        def fetch_rates():
            try:
                if API_KEY and API_KEY != "demo":
                    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
                    urleur = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/EUR"
                    
                    response = requests.get(url)
                    response2 = requests.get(urleur)
                    
                    if response.status_code == 200 and response2.status_code == 200:
                        self.api_data = response.json()
                        self.api_data_eur = response2.json()
                        print('✅ Курсы валют успешно загружены из API')
                    else:
                        print('⚠️ Ошибка загрузки из API, использую локальные курсы')
                        self.use_local_rates()
                else:
                    print('⚠️ API ключ не найден, использую локальные курсы')
                    self.use_local_rates()
                    
            except Exception as e:
                print(f'⚠️ Ошибка: {e}, использую локальные курсы')
                self.use_local_rates()
            
            # Обновляем интерфейс после загрузки
            self.root.after(0, self.update_rates_info)
        
        # Запуск в отдельном потоке
        thread = Thread(target=fetch_rates)
        thread.daemon = True
        thread.start()
    
    def use_local_rates(self):
        """Использование локальных курсов"""
        self.api_data = {
            "conversion_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "RUB": 90.0,  # 1 USD = 90 RUB
            }
        }
        
        self.api_data_eur = {
            "conversion_rates": {
                "USD": 1.18,
                "EUR": 1.0,
                "RUB": 105.0,  # 1 EUR = 105 RUB
            }
        }
        print('📊 Использую локальные курсы валют')
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # ===== ЗАГОЛОВОК =====
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(title_frame, text="💱 Универсальный конвертер валют", 
                 font=('Arial', 18, 'bold')).pack()
        
        ttk.Label(title_frame, text="Поддерживает современные и исторические валюты", 
                 font=('Arial', 10), foreground='gray').pack()
        
        # ===== ВЫБОР ВАЛЮТ =====
        currency_frame = ttk.LabelFrame(main_frame, text="Выберите валюты", 
                                       padding="15")
        currency_frame.pack(fill="x", pady=(0, 15))
        
        # Доступные валюты
        self.currencies = ['USD', 'EUR', 'RUB', 'USSR RUB', 'RUS EMPIRE RUB']
        
        # Исходная валюта
        ttk.Label(currency_frame, text="Из:", font=('Arial', 11)).grid(
            row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.from_currency = ttk.Combobox(currency_frame, values=self.currencies, 
                                         width=20, state="readonly", font=('Arial', 11))
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        self.from_currency.set('USD')
        self.from_currency.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # Информация о валюте
        self.label_from_info = ttk.Label(currency_frame, text="Доллар США", 
                                        font=('Arial', 9), foreground='gray')
        self.label_from_info.grid(row=0, column=2, padx=10)
        
        # Целевая валюта
        ttk.Label(currency_frame, text="В:", font=('Arial', 11)).grid(
            row=1, column=0, sticky='w', padx=5, pady=5)
        
        self.to_currency = ttk.Combobox(currency_frame, values=self.currencies, 
                                       width=20, state="readonly", font=('Arial', 11))
        self.to_currency.grid(row=1, column=1, padx=5, pady=5)
        self.to_currency.set('RUB')
        self.to_currency.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # Информация о валюте
        self.label_to_info = ttk.Label(currency_frame, text="Российский рубль", 
                                      font=('Arial', 9), foreground='gray')
        self.label_to_info.grid(row=1, column=2, padx=10)
        
        # Кнопка "Поменять местами"
        swap_btn = ttk.Button(currency_frame, text="⇄ Поменять местами", 
                             command=self.swap_currencies)
        swap_btn.grid(row=2, column=0, columnspan=3, pady=10)
        
        # ===== ВВОД СУММЫ =====
        amount_frame = ttk.LabelFrame(main_frame, text="Сумма", padding="10")
        amount_frame.pack(fill="x", pady=(0, 15))
        
        # Поле ввода
        input_frame = ttk.Frame(amount_frame)
        input_frame.pack(fill="x")
        
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, 
                                font=('Arial', 14), width=15)
        amount_entry.pack(side='left', padx=5)
        amount_entry.bind('<KeyRelease>', self.on_amount_change)
        amount_entry.bind('<Return>', lambda e: self.convert())
        
        # Быстрые суммы
        quick_frame = ttk.Frame(amount_frame)
        quick_frame.pack(fill="x", pady=(5, 0))
        
        for value in [10, 50, 100, 500, 1000]:
            btn = ttk.Button(quick_frame, text=str(value), 
                           command=lambda v=value: self.set_amount(v))
            btn.pack(side='left', padx=2)
        
        # ===== КНОПКА КОНВЕРТАЦИИ =====
        convert_btn = ttk.Button(main_frame, text="🔄 Конвертировать", 
                                command=self.convert)
        convert_btn.pack(pady=(0, 15))
        
        # ===== РЕЗУЛЬТАТ =====
        result_frame = ttk.LabelFrame(main_frame, text="Результат", padding="15")
        result_frame.pack(fill="both", expand=True)
        
        self.result_var = tk.StringVar()
        result_label = ttk.Label(result_frame, textvariable=self.result_var, 
                                font=('Arial', 18, 'bold'), foreground='blue')
        result_label.pack(pady=10)
        
        # Детали курса
        self.rate_var = tk.StringVar()
        rate_label = ttk.Label(result_frame, textvariable=self.rate_var, 
                              font=('Arial', 12), foreground='darkgreen')
        rate_label.pack()
        
        # ===== ИНФОРМАЦИЯ О КУРСАХ =====
        info_frame = ttk.LabelFrame(main_frame, text="📊 Актуальные курсы валют", 
                                   padding="15")
        info_frame.pack(fill="x", pady=(15, 0))
        
        # Создаем текстовый виджет для курсов
        self.rates_text = tk.Text(info_frame, height=9, font=('Arial', 11), 
                                 bg='#f0f0f0', relief='sunken', bd=2)
        self.rates_text.pack(fill="x", pady=5)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(info_frame, orient='vertical', 
                                 command=self.rates_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.rates_text.config(yscrollcommand=scrollbar.set)
        
        # ===== ИСТОРИЯ КОНВЕРТАЦИЙ =====
        history_frame = ttk.LabelFrame(main_frame, text="📜 История конвертаций", 
                                      padding="10")
        history_frame.pack(fill="x", pady=(10, 0))
        
        self.history_list = tk.Listbox(history_frame, height=4, font=('Arial', 10))
        self.history_list.pack(fill="x")
        
        # Кнопка очистки истории
        clear_btn = ttk.Button(history_frame, text="🗑 Очистить историю", 
                              command=self.clear_history)
        clear_btn.pack(pady=(5, 0))
        
        # Обновление информации
        self.update_currency_info()
        self.root.after(1000, self.update_rates_info)
    
    def on_currency_change(self, event=None):
        """Обновление информации при смене валюты"""
        self.update_currency_info()
    
    def update_currency_info(self):
        """Обновление информации о выбранных валютах"""
        currency_names = {
            'USD': 'Доллар США',
            'EUR': 'Евро',
            'RUB': 'Российский рубль',
            'USSR RUB': 'Советский рубль',
            'RUS EMPIRE RUB': 'Рубль империи'
        }
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        self.label_from_info.config(text=currency_names.get(from_curr, ''))
        self.label_to_info.config(text=currency_names.get(to_curr, ''))
        
        # Обновить курс
        if from_curr and to_curr and from_curr != to_curr:
            rate = self.get_rate(from_curr, to_curr)
            if rate is not None:
                self.rate_var.set(f"1 {from_curr} = {rate:.6f} {to_curr}")
            else:
                self.rate_var.set("Курс не доступен")
    
    def get_rate(self, from_curr, to_curr):
        """Получение курса между двумя валютами с учетом исторических"""
        # Если обе валюты - исторические
        if from_curr in self.historical_rates and to_curr in self.historical_rates:
            if from_curr == "USSR RUB" and to_curr == "RUS EMPIRE RUB":
                return self.historical_rates["USSR RUB"] / self.historical_rates["RUS EMPIRE RUB"]
            elif from_curr == "RUS EMPIRE RUB" and to_curr == "USSR RUB":
                return self.historical_rates["RUS EMPIRE RUB"] / self.historical_rates["USSR RUB"]
        
        # Если from_curr историческая, to_curr современная
        if from_curr in self.historical_rates and to_curr not in self.historical_rates:
            if not self.api_data:
                return None
            rates = self.api_data['conversion_rates']
            if 'RUB' not in rates:
                return None
            
            rub_amount = self.historical_rates[from_curr]
            if to_curr in rates:
                return rub_amount * rates[to_curr] / rates['RUB']
        
        # Если from_curr современная, to_curr историческая
        if from_curr not in self.historical_rates and to_curr in self.historical_rates:
            if not self.api_data:
                return None
            rates = self.api_data['conversion_rates']
            if 'RUB' not in rates:
                return None
            
            rub_amount = 1 / rates[from_curr] * rates['RUB']
            return rub_amount / self.historical_rates[to_curr]
        
        # Обычные валюты
        if not self.api_data:
            return None
        
        rates = self.api_data['conversion_rates']
        if from_curr in rates and to_curr in rates:
            return rates[to_curr] / rates[from_curr]
        
        return None
    
    def swap_currencies(self):
        """Поменять местами валюты"""
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        if from_curr and to_curr:
            self.from_currency.set(to_curr)
            self.to_currency.set(from_curr)
            self.update_currency_info()
            if self.amount_var.get():
                self.convert()
    
    def set_amount(self, value):
        """Установить быструю сумму"""
        self.amount_var.set(str(value))
        self.convert()
    
    def on_amount_change(self, event=None):
        """Автоконвертация при изменении суммы"""
        pass
    
    def convert(self):
        """Выполнение конвертации"""
        try:
            amount_text = self.amount_var.get().replace(',', '.')
            if not amount_text:
                return
            
            amount = float(amount_text)
            if amount < 0:
                messagebox.showerror("Ошибка", "Сумма не может быть отрицательной")
                return
            
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()
            
            if not from_curr or not to_curr:
                messagebox.showerror("Ошибка", "Выберите обе валюты")
                return
            
            result = self.calculate_conversion(amount, from_curr, to_curr)
            
            if result is not None:
                self.result_var.set(f"{amount:,.2f} {from_curr} = {result:,.2f} {to_curr}")
                
                # Добавить в историю
                history_entry = f"{amount:.2f} {from_curr} → {result:.2f} {to_curr}"
                self.history_list.insert(0, history_entry)
                if self.history_list.size() > 10:
                    self.history_list.delete(10)
            else:
                messagebox.showerror("Ошибка", 
                                    "Не удалось выполнить конвертацию для выбранных валют")
                
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при конвертации: {e}")
    
    def calculate_conversion(self, amount, from_curr, to_curr):
        """Расчет конвертации между валютами с учетом исторических"""
        if from_curr == to_curr:
            return amount
        
        # Если обе валюты - исторические
        if from_curr in self.historical_rates and to_curr in self.historical_rates:
            if from_curr == "USSR RUB" and to_curr == "RUS EMPIRE RUB":
                return amount * (self.historical_rates["USSR RUB"] / self.historical_rates["RUS EMPIRE RUB"])
            elif from_curr == "RUS EMPIRE RUB" and to_curr == "USSR RUB":
                return amount * (self.historical_rates["RUS EMPIRE RUB"] / self.historical_rates["USSR RUB"])
        
        # Если from_curr историческая, to_curr современная
        if from_curr in self.historical_rates and to_curr not in self.historical_rates:
            if not self.api_data:
                return None
            rates = self.api_data['conversion_rates']
            if 'RUB' not in rates or to_curr not in rates:
                return None
            
            rub_amount = amount * self.historical_rates[from_curr]
            return rub_amount * rates[to_curr] / rates['RUB']
        
        # Если from_curr современная, to_curr историческая
        if from_curr not in self.historical_rates and to_curr in self.historical_rates:
            if not self.api_data:
                return None
            rates = self.api_data['conversion_rates']
            if 'RUB' not in rates or from_curr not in rates:
                return None
            
            rub_amount = amount / rates[from_curr] * rates['RUB']
            return rub_amount / self.historical_rates[to_curr]
        
        # Обычные валюты
        if not self.api_data:
            return None
        
        rates = self.api_data['conversion_rates']
        if from_curr in rates and to_curr in rates:
            return (amount / rates[from_curr]) * rates[to_curr]
        
        return None
    
    def update_rates_info(self):
        """Обновление информации о текущих курсах (ИСПРАВЛЕНО)"""
        self.rates_text.delete(1.0, tk.END)
        
        if self.api_data:
            rates = self.api_data['conversion_rates']
            
            # Заголовок
            self.rates_text.insert(tk.END, "=" * 55 + "\n", "header")
            self.rates_text.insert(tk.END, "  СОВРЕМЕННЫЕ КУРСЫ\n", "header")
            self.rates_text.insert(tk.END, "=" * 55 + "\n\n", "header")
            
            # Правильное отображение курсов
            if 'USD' in rates and 'RUB' in rates:
                usd_to_rub = rates['RUB']  # 1 USD = X RUB
                self.rates_text.insert(tk.END, f"  💵 1 USD = {usd_to_rub:.2f} RUB\n", "rate")
            
            if 'EUR' in rates and 'RUB' in rates:
                eur_to_rub = rates['RUB'] / rates['EUR']  # 1 EUR = X RUB
                self.rates_text.insert(tk.END, f"  💶 1 EUR = {eur_to_rub:.2f} RUB\n", "rate")
            
            if 'USD' in rates and 'EUR' in rates:
                usd_to_eur = rates['EUR']  # 1 USD = X EUR
                self.rates_text.insert(tk.END, f"  💵 1 USD = {usd_to_eur:.4f} EUR\n", "rate")
            
            self.rates_text.insert(tk.END, "\n" + "=" * 55 + "\n", "header")
            self.rates_text.insert(tk.END, "  ИСТОРИЧЕСКИЕ КУРСЫ (к RUS RUB)\n", "header")
            self.rates_text.insert(tk.END, "=" * 55 + "\n\n", "header")
            
            # Исторические курсы
            self.rates_text.insert(tk.END, f"  🏛 1 USSR RUB = {self.historical_rates['USSR RUB']:.2f} RUS RUB\n", "historical")
            self.rates_text.insert(tk.END, f"  🏛 1 RUS EMPIRE RUB = {self.historical_rates['RUS EMPIRE RUB']:.2f} RUS RUB\n", "historical")
            
            # Конвертация исторических в USD
            if 'RUB' in rates and 'USD' in rates:
                rub_to_usd = 1 / rates['RUB']
                
                self.rates_text.insert(tk.END, "\n" + "=" * 55 + "\n", "header")
                self.rates_text.insert(tk.END, "  ИСТОРИЧЕСКИЕ КУРСЫ (к USD)\n", "header")
                self.rates_text.insert(tk.END, "=" * 55 + "\n\n", "header")
                
                ussr_to_usd = self.historical_rates['USSR RUB'] * rub_to_usd
                empire_to_usd = self.historical_rates['RUS EMPIRE RUB'] * rub_to_usd
                
                self.rates_text.insert(tk.END, f"  🏛 1 USSR RUB = {ussr_to_usd:.4f} USD\n", "historical_usd")
                self.rates_text.insert(tk.END, f"  🏛 1 RUS EMPIRE RUB = {empire_to_usd:.4f} USD\n", "historical_usd")
            
            # Настройка цветов
            self.rates_text.tag_config("header", foreground='darkblue', font=('Arial', 11, 'bold'))
            self.rates_text.tag_config("rate", foreground='darkgreen', font=('Arial', 10))
            self.rates_text.tag_config("historical", foreground='darkred', font=('Arial', 10, 'bold'))
            self.rates_text.tag_config("historical_usd", foreground='purple', font=('Arial', 10, 'bold'))
            
            self.rates_text.config(state='disabled')
        else:
            self.rates_text.insert(tk.END, "⏳ Загрузка курсов...", "loading")
            self.rates_text.tag_config("loading", foreground='gray', font=('Arial', 11))
            self.rates_text.config(state='disabled')
        
        # Повторное обновление через 10 секунд
        self.root.after(10000, self.update_rates_info)
    
    def clear_history(self):
        """Очистка истории конвертаций"""
        self.history_list.delete(0, tk.END)
    
    def load_settings(self):
        """Загрузка сохраненных настроек"""
        try:
            if os.path.exists("converter_settings.json"):
                with open("converter_settings.json", "r") as f:
                    settings = json.load(f)
                    if "from" in settings:
                        self.from_currency.set(settings["from"])
                    if "to" in settings:
                        self.to_currency.set(settings["to"])
                    if "history" in settings:
                        for item in settings["history"][:10]:
                            self.history_list.insert(tk.END, item)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            settings = {
                "from": self.from_currency.get(),
                "to": self.to_currency.get(),
                "history": list(self.history_list.get(0, tk.END))
            }
            with open("converter_settings.json", "w") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

# ==================== ЗАПУСК ====================
def main():
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_settings(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()
