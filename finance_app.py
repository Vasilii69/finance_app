"""
ПРИЛОЖЕНИЕ ДЛЯ УЧЁТА ЛИЧНЫХ ФИНАНСОВ
Версия 2.0 с улучшенным интерфейсом
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Инициализация colorama для Windows
init(autoreset=True)

class FinancialApp:
    """
    Главный класс приложения для управления финансами
    """
    
    def __init__(self, data_file: str = "finance_data.json"):
        """
        Инициализация приложения
        
        Args:
            data_file: путь к файлу для хранения данных
        """
        self.data_file = data_file
        self.transactions = []  # список всех транзакций
        self.categories = {     # категории доходов и расходов
            'income': ['Зарплата', 'Фриланс', 'Подарки', 'Инвестиции', 'Другое'],
            'expense': ['Продукты', 'Транспорт', 'Развлечения', 'Коммунальные', 
                       'Здоровье', 'Одежда', 'Образование', 'Другое']
        }
        self.budgets = {}  # бюджеты по категориям
        self.load_data()  # загружаем данные при старте
        self.show_splash_screen()
    
    # ====================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ======================
    
    def print_header(self, text: str, color=Fore.CYAN):
        """Красивый заголовок с цветом"""
        print("\n" + "="*60)
        print(f"{color}{text:^60}{Style.RESET_ALL}")
        print("="*60)
    
    def print_success(self, text: str):
        """Зеленое сообщение об успехе"""
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
    
    def print_error(self, text: str):
        """Красное сообщение об ошибке"""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
    
    def print_warning(self, text: str):
        """Желтое предупреждение"""
        print(f"{Fore.YELLOW}⚠️ {text}{Style.RESET_ALL}")
    
    def print_info(self, text: str):
        """Синее информационное сообщение"""
        print(f"{Fore.BLUE}ℹ️ {text}{Style.RESET_ALL}")
    
    def print_menu_item(self, number: str, text: str, color=Fore.WHITE):
        """Цветной пункт меню"""
        print(f"  {Fore.YELLOW}{number}{Style.RESET_ALL}. {color}{text}{Style.RESET_ALL}")
    
    def ask_yes_no(self, question: str) -> bool:
        """Умный вопрос с поддержкой разных вариантов ответа"""
        while True:
            answer = input(f"{question} (д/н): ").lower().strip()
            if answer in ['д', 'да', 'y', 'yes', '1', '+']:
                return True
            if answer in ['н', 'нет', 'n', 'no', '0', '-']:
                return False
            self.print_error("Пожалуйста, ответьте 'д' или 'н'")
    
    def select_from_list(self, items: list, prompt: str = "Выберите пункт") -> int:
        """Умный выбор из списка с валидацией"""
        while True:
            try:
                choice = int(input(f"{prompt}: "))
                if 1 <= choice <= len(items):
                    return choice
                else:
                    self.print_error(f"Введите число от 1 до {len(items)}")
            except ValueError:
                self.print_error("Введите число")
    
    def smart_date_input(self):
        """Умный ввод даты с подсказками"""
        print("\n📅 Выберите дату:")
        print("  1. Сегодня")
        print("  2. Вчера")
        print("  3. На этой неделе")
        print("  4. В этом месяце")
        print("  5. Другая дата")
        
        choice = self.select_from_list(list(range(1,6)))
        
        if choice == 1:
            return datetime.now()
        elif choice == 2:
            return datetime.now() - timedelta(days=1)
        elif choice == 3:
            # Возвращаем понедельник текущей недели
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            return monday
        elif choice == 4:
            # Первое число текущего месяца
            return datetime.now().replace(day=1)
        else:
            while True:
                try:
                    date_str = input("Введите дату (ДД.ММ.ГГГГ): ")
                    return datetime.strptime(date_str, "%d.%m.%Y")
                except ValueError:
                    self.print_error("Неверный формат. Используйте ДД.ММ.ГГГГ")
    
    def show_splash_screen(self):
        """Красивый экран приветствия"""
        splash = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                              ║
║   🏦 {Fore.YELLOW}ЛИЧНЫЙ ФИНАНСОВЫЙ УЧЁТ v2.0{Fore.CYAN}                           ║
║                                                              ║
║   {Fore.GREEN}💰 Контролируйте свои доходы и расходы{Fore.CYAN}                    ║
║   {Fore.BLUE}📊 Анализируйте траты с помощью графиков{Fore.CYAN}                  ║
║   {Fore.MAGENTA}🎯 Достигайте финансовых целей{Fore.CYAN}                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(splash)
        time.sleep(1)
    
    def auto_save(self):
        """Автосохранение с индикацией"""
        print(f"{Fore.YELLOW}💾 Сохранение", end="")
        for _ in range(3):
            time.sleep(0.3)
            print(".", end="", flush=True)
        self.save_data()
        print(f"{Fore.GREEN} Готово!{Style.RESET_ALL}")
    
    def show_budget_progress(self, spent: float, budget: float, category: str):
        """Показывает прогресс-бар для бюджета категории"""
        if budget <= 0:
            return
            
        percentage = (spent / budget) * 100
        bar_length = 30
        filled = int(bar_length * percentage / 100)
        
        bar = "█" * filled + "░" * (bar_length - filled)
        
        if percentage < 50:
            color = Fore.GREEN
        elif percentage < 80:
            color = Fore.YELLOW
        else:
            color = Fore.RED
        
        print(f"\n{category}:")
        print(f"[{color}{bar}{Style.RESET_ALL}] {percentage:.1f}%")
        print(f"Потрачено: {spent:.2f} ₽ из {budget:.2f} ₽")
    
    def _display_transactions(self, transactions):
        """Внутренний метод для отображения списка транзакций"""
        if not transactions:
            self.print_warning("Нет транзакций для отображения")
            return
        
        # Подготовка данных для таблицы
        table_data = []
        for t in sorted(transactions, key=lambda x: x['date'], reverse=True):
            date_str = t['date'].strftime("%d.%m.%Y")
            type_str = f"{Fore.GREEN}Доход{Style.RESET_ALL}" if t['type'] == 'income' else f"{Fore.RED}Расход{Style.RESET_ALL}"
            amount_str = f"{t['amount']:.2f} ₽"
            if t['type'] == 'expense':
                amount_str = f"{Fore.RED}{amount_str}{Style.RESET_ALL}"
            else:
                amount_str = f"{Fore.GREEN}{amount_str}{Style.RESET_ALL}"
            
            description = t['description']
            if len(description) > 30:
                description = description[:27] + "..."
            
            table_data.append([
                date_str,
                type_str,
                t['category'],
                amount_str,
                description
            ])
        
        headers = ["Дата", "Тип", "Категория", "Сумма", "Описание"]
        print(tabulate(table_data, headers=headers, tablefmt="grid", stralign="left"))
    
    # ====================== РАБОТА С ДАННЫМИ ======================
    
    def load_data(self) -> None:
        """Загрузка данных из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.transactions = data.get('transactions', [])
                    self.budgets = data.get('budgets', {})
                    # Преобразуем строки дат обратно в объекты datetime
                    for transaction in self.transactions:
                        transaction['date'] = datetime.fromisoformat(transaction['date'])
                self.print_success("Данные успешно загружены")
            except Exception as e:
                self.print_error(f"Ошибка загрузки данных: {e}")
                self.transactions = []
                self.budgets = {}
        else:
            self.print_info("Файл с данными не найден. Будет создан новый при сохранении.")
    
    def save_data(self) -> None:
        """Сохранение данных в файл"""
        try:
            # Преобразуем datetime в строку для JSON
            transactions_to_save = []
            for transaction in self.transactions:
                transaction_copy = transaction.copy()
                transaction_copy['date'] = transaction['date'].isoformat()
                transactions_to_save.append(transaction_copy)
            
            data = {
                'transactions': transactions_to_save,
                'budgets': self.budgets
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            self.print_success("Данные успешно сохранены")
        except Exception as e:
            self.print_error(f"Ошибка сохранения данных: {e}")
    
    # ====================== ОСНОВНЫЕ ФУНКЦИИ ======================
    
    def add_transaction(self) -> None:
        """
        Добавление новой транзакции (дохода или расхода)
        """
        self.print_header("➕ ДОБАВЛЕНИЕ ТРАНЗАКЦИИ", Fore.GREEN)
        
        # Выбор типа транзакции
        while True:
            transaction_type = input("Выберите тип (1 - доход, 2 - расход): ").strip()
            if transaction_type in ['1', '2']:
                transaction_type = 'income' if transaction_type == '1' else 'expense'
                break
            self.print_error("Пожалуйста, введите 1 или 2")
        
        # Выбор категории
        print(f"\n📊 Доступные категории для {'дохода' if transaction_type == 'income' else 'расхода'}:")
        categories = self.categories[transaction_type]
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")
        
        while True:
            try:
                category_choice = int(input("\nВыберите номер категории: "))
                if 1 <= category_choice <= len(categories):
                    category = categories[category_choice - 1]
                    break
                else:
                    self.print_error(f"Введите число от 1 до {len(categories)}")
            except ValueError:
                self.print_error("Пожалуйста, введите число")
        
        # Ввод суммы
        while True:
            try:
                amount = float(input("Введите сумму: "))
                if amount <= 0:
                    self.print_error("Сумма должна быть положительной")
                else:
                    break
            except ValueError:
                self.print_error("Пожалуйста, введите число")
        
        # Ввод описания
        description = input("Введите описание (необязательно): ").strip()
        
        # Ввод даты
        use_current = self.ask_yes_no("Использовать текущую дату?")
        if use_current:
            date = datetime.now()
        else:
            date = self.smart_date_input()
        
        # Создаем транзакцию
        transaction = {
            'type': transaction_type,
            'category': category,
            'amount': amount,
            'description': description,
            'date': date
        }
        
        self.transactions.append(transaction)
        self.print_success("Транзакция успешно добавлена!")
        
        # Проверяем бюджет для расходов
        if transaction_type == 'expense' and category in self.budgets:
            spent = sum(t['amount'] for t in self.transactions 
                       if t['type'] == 'expense' and t['category'] == category)
            self.show_budget_progress(spent, self.budgets[category], category)
        
        self.auto_save()
    
    def view_balance(self) -> None:
        """
        Просмотр текущего баланса и статистики
        """
        self.print_header("💰 ТЕКУЩИЙ БАЛАНС", Fore.CYAN)
        
        total_income = sum(t['amount'] for t in self.transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
        balance = total_income - total_expense
        
        # Цвет для баланса
        balance_color = Fore.GREEN if balance >= 0 else Fore.RED
        
        print(f"\n{Fore.GREEN}💵 Общий доход:{Style.RESET_ALL}     {total_income:>15.2f} ₽")
        print(f"{Fore.RED}💸 Общие расходы:{Style.RESET_ALL}   {total_expense:>15.2f} ₽")
        print(f"{balance_color}💰 Текущий баланс:{Style.RESET_ALL}  {balance:>15.2f} ₽")
        
        # Статистика по категориям расходов
        if total_expense > 0:
            print(f"\n{Fore.YELLOW}📊 РАСХОДЫ ПО КАТЕГОРИЯМ:{Style.RESET_ALL}")
            expense_by_category = {}
            for t in self.transactions:
                if t['type'] == 'expense':
                    expense_by_category[t['category']] = expense_by_category.get(t['category'], 0) + t['amount']
            
            # Сортируем по убыванию суммы
            sorted_expenses = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)
            
            for category, amount in sorted_expenses:
                percentage = (amount / total_expense) * 100
                bar_length = int(percentage / 2)  # Максимум 50 символов
                bar = "█" * bar_length
                print(f"  {category:15} {amount:>8.2f} ₽ ({percentage:5.1f}%) {Fore.GREEN}{bar}{Style.RESET_ALL}")
        
        # Проверка бюджетов
        if self.budgets:
            print(f"\n{Fore.YELLOW}🎯 БЮДЖЕТЫ:{Style.RESET_ALL}")
            for category, budget in self.budgets.items():
                spent = sum(t['amount'] for t in self.transactions 
                           if t['type'] == 'expense' and t['category'] == category)
                self.show_budget_progress(spent, budget, category)
    
    def view_transactions(self) -> None:
        """
        Просмотр всех транзакций с фильтрацией
        """
        self.print_header("📋 ИСТОРИЯ ТРАНЗАКЦИЙ", Fore.BLUE)
        
        if not self.transactions:
            self.print_warning("Нет транзакций для отображения")
            return
        
        # Фильтры
        print(f"\n{Fore.YELLOW}🔍 Фильтры (можно пропустить, нажав Enter):{Style.RESET_ALL}")
        
        # Фильтр по типу
        type_filter = input("Тип (1 - доходы, 2 - расходы, Enter - все): ").strip()
        if type_filter == '1':
            filtered = [t for t in self.transactions if t['type'] == 'income']
        elif type_filter == '2':
            filtered = [t for t in self.transactions if t['type'] == 'expense']
        else:
            filtered = self.transactions.copy()
        
        # Фильтр по категории
        if filtered:
            available_categories = set(t['category'] for t in filtered)
            print(f"\nДоступные категории: {', '.join(available_categories)}")
            category_filter = input("Категория (Enter - все): ").strip()
            if category_filter:
                filtered = [t for t in filtered if t['category'].lower() == category_filter.lower()]
        
        # Отображение
        self._display_transactions(filtered)
        
        # Итоги по отфильтрованным
        if filtered:
            total = sum(t['amount'] for t in filtered)
            print(f"\n{Fore.CYAN}Итого по выбранным: {total:.2f} ₽{Style.RESET_ALL}")
    
    def search_transactions(self):
        """Умный поиск по транзакциям"""
        self.print_header("🔍 ПОИСК ТРАНЗАКЦИЙ", Fore.CYAN)
        
        if not self.transactions:
            self.print_warning("Нет транзакций для поиска")
            return
        
        print("Искать по:")
        print("  1. Описанию")
        print("  2. Категории")
        print("  3. Сумме (больше чем)")
        print("  4. Сумме (меньше чем)")
        print("  5. Дате")
        print("  6. Типу (доходы/расходы)")
        
        choice = self.select_from_list(list(range(1,7)))
        
        results = []
        if choice == 1:
            query = input("Введите текст для поиска: ").lower()
            results = [t for t in self.transactions if query in t['description'].lower()]
            self.print_success(f"Найдено по описанию '{query}': {len(results)}")
        
        elif choice == 2:
            query = input("Введите категорию: ").lower()
            results = [t for t in self.transactions if query in t['category'].lower()]
            self.print_success(f"Найдено в категории '{query}': {len(results)}")
        
        elif choice == 3:
            min_amount = float(input("Минимальная сумма: "))
            results = [t for t in self.transactions if t['amount'] >= min_amount]
            self.print_success(f"Найдено с суммой ≥ {min_amount}: {len(results)}")
        
        elif choice == 4:
            max_amount = float(input("Максимальная сумма: "))
            results = [t for t in self.transactions if t['amount'] <= max_amount]
            self.print_success(f"Найдено с суммой ≤ {max_amount}: {len(results)}")
        
        elif choice == 5:
            date_str = input("Введите дату (ДД.ММ.ГГГГ): ")
            try:
                search_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                results = [t for t in self.transactions if t['date'].date() == search_date]
                self.print_success(f"Найдено за {date_str}: {len(results)}")
            except ValueError:
                self.print_error("Неверный формат даты")
                return
        
        elif choice == 6:
            print("Тип: 1 - доходы, 2 - расходы")
            type_choice = input("Выберите: ")
            if type_choice == '1':
                results = [t for t in self.transactions if t['type'] == 'income']
                self.print_success(f"Найдено доходов: {len(results)}")
            elif type_choice == '2':
                results = [t for t in self.transactions if t['type'] == 'expense']
                self.print_success(f"Найдено расходов: {len(results)}")
        
        if results:
            self._display_transactions(results)
        else:
            self.print_warning("Ничего не найдено")
    
    def show_statistics(self) -> None:
        """
        Показывает расширенную статистику и графики
        """
        self.print_header("📊 СТАТИСТИКА", Fore.MAGENTA)
        
        if not self.transactions:
            self.print_warning("Недостаточно данных для статистики")
            return
        
        # Статистика по месяцам
        print(f"\n{Fore.YELLOW}📅 СТАТИСТИКА ПО МЕСЯЦАМ:{Style.RESET_ALL}")
        
        monthly_stats = {}
        for t in self.transactions:
            month_key = t['date'].strftime("%Y-%m")
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'income': 0, 'expense': 0}
            monthly_stats[month_key][t['type']] += t['amount']
        
        # Таблица по месяцам
        month_data = []
        for month in sorted(monthly_stats.keys()):
            income = monthly_stats[month]['income']
            expense = monthly_stats[month]['expense']
            balance = income - expense
            
            # Цвет для баланса
            balance_color = Fore.GREEN if balance >= 0 else Fore.RED
            
            month_data.append([
                month,
                f"{Fore.GREEN}{income:.2f} ₽{Style.RESET_ALL}",
                f"{Fore.RED}{expense:.2f} ₽{Style.RESET_ALL}",
                f"{balance_color}{balance:.2f} ₽{Style.RESET_ALL}"
            ])
        
        headers = ["Месяц", "Доходы", "Расходы", "Баланс"]
        print(tabulate(month_data, headers=headers, tablefmt="grid"))
        
        # Спрашиваем, хочет ли пользователь увидеть график
        if self.ask_yes_no("\n📈 Показать график расходов по категориям?"):
            self.plot_expenses_by_category()
        
        # Управление бюджетами
        if self.ask_yes_no("\n🎯 Управлять бюджетами?"):
            self.manage_budgets()
    
    def plot_expenses_by_category(self) -> None:
        """
        Улучшенная визуализация с красивыми цветами
        """
        expenses = [t for t in self.transactions if t['type'] == 'expense']
        
        if not expenses:
            self.print_warning("Нет данных о расходах для построения графика")
            return
        
        # Собираем данные по категориям
        category_expenses = {}
        for t in expenses:
            category_expenses[t['category']] = category_expenses.get(t['category'], 0) + t['amount']
        
        # Подготовка данных
        categories = list(category_expenses.keys())
        amounts = list(category_expenses.values())
        
        # Красивые цвета для диаграммы
        colors = plt.cm.Set3(range(len(categories)))
        
        # Создание графика
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Круговая диаграмма
        wedges, texts, autotexts = ax1.pie(amounts, labels=categories, autopct='%1.1f%%',
                                            colors=colors, startangle=90)
        ax1.set_title('Распределение расходов по категориям', fontsize=14, fontweight='bold')
        
        # Добавляем легенду с суммами
        legend_labels = [f'{cat}: {amt:.2f} ₽' for cat, amt in zip(categories, amounts)]
        ax1.legend(wedges, legend_labels, title="Категории", 
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        # Столбчатая диаграмма
        bars = ax2.bar(categories, amounts, color=colors)
        ax2.set_title('Суммы по категориям', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Сумма (₽)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Добавляем значения на столбцы
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{amount:.0f} ₽', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def manage_budgets(self):
        """Управление бюджетами по категориям"""
        self.print_header("🎯 УПРАВЛЕНИЕ БЮДЖЕТАМИ", Fore.YELLOW)
        
        print("1. Просмотреть бюджеты")
        print("2. Установить бюджет")
        print("3. Удалить бюджет")
        print("4. Назад")
        
        choice = self.select_from_list(list(range(1,5)))
        
        if choice == 1:
            if not self.budgets:
                self.print_warning("Бюджеты не установлены")
            else:
                for category, budget in self.budgets.items():
                    spent = sum(t['amount'] for t in self.transactions 
                               if t['type'] == 'expense' and t['category'] == category)
                    self.show_budget_progress(spent, budget, category)
        
        elif choice == 2:
            # Показываем доступные категории расходов
            print("\nДоступные категории расходов:")
            expense_categories = self.categories['expense']
            for i, cat in enumerate(expense_categories, 1):
                print(f"  {i}. {cat}")
            
            cat_choice = self.select_from_list(expense_categories, "Выберите категорию")
            category = expense_categories[cat_choice - 1]
            
            try:
                budget = float(input(f"Введите бюджет для '{category}': "))
                if budget > 0:
                    self.budgets[category] = budget
                    self.print_success(f"Бюджет для '{category}' установлен: {budget:.2f} ₽")
                    self.auto_save()
                else:
                    self.print_error("Бюджет должен быть положительным")
            except ValueError:
                self.print_error("Введите число")
        
        elif choice == 3:
            if not self.budgets:
                self.print_warning("Нет установленных бюджетов")
            else:
                print("\nУстановленные бюджеты:")
                categories = list(self.budgets.keys())
                for i, cat in enumerate(categories, 1):
                    print(f"  {i}. {cat}: {self.budgets[cat]:.2f} ₽")
                
                cat_choice = self.select_from_list(categories, "Выберите бюджет для удаления")
                category = categories[cat_choice - 1]
                del self.budgets[category]
                self.print_success(f"Бюджет для '{category}' удален")
                self.auto_save()
    
    def delete_transaction(self) -> None:
        """
        Удаление транзакции
        """
        self.print_header("🗑️ УДАЛЕНИЕ ТРАНЗАКЦИИ", Fore.RED)
        
        if not self.transactions:
            self.print_warning("Нет транзакций для удаления")
            return
        
        # Показываем последние 10 транзакций
        print("\nПоследние транзакции:")
        recent = sorted(self.transactions, key=lambda x: x['date'], reverse=True)[:10]
        
        table_data = []
        for i, t in enumerate(recent, 1):
            date_str = t['date'].strftime("%d.%m.%Y")
            type_str = "Доход" if t['type'] == 'income' else "Расход"
            amount_str = f"{t['amount']:.2f} ₽"
            table_data.append([
                i,
                date_str,
                type_str,
                t['category'],
                amount_str,
                t['description'][:20]
            ])
        
        headers = ["№", "Дата", "Тип", "Категория", "Сумма", "Описание"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        try:
            choice = int(input("\nВведите номер транзакции для удаления (0 - отмена): "))
            if choice == 0:
                return
            if 1 <= choice <= len(recent):
                transaction_to_delete = recent[choice - 1]
                
                # Находим и удаляем транзакцию
                for i, t in enumerate(self.transactions):
                    if (t['date'] == transaction_to_delete['date'] and 
                        t['amount'] == transaction_to_delete['amount'] and
                        t['category'] == transaction_to_delete['category']):
                        del self.transactions[i]
                        self.print_success("Транзакция удалена")
                        self.auto_save()
                        break
            else:
                self.print_error("Неверный номер")
        except ValueError:
            self.print_error("Пожалуйста, введите число")
    
    def run(self) -> None:
        """
        Главный цикл приложения
        """
        while True:
            self.print_header("🏦 ЛИЧНЫЙ ФИНАНСОВЫЙ УЧЁТ", Fore.MAGENTA)
            
            menu_items = [
                ("1", "➕ Добавить транзакцию", Fore.GREEN),
                ("2", "💰 Посмотреть баланс", Fore.CYAN),
                ("3", "📋 История транзакций", Fore.BLUE),
                ("4", "🔍 Поиск транзакций", Fore.YELLOW),
                ("5", "📊 Статистика и графики", Fore.MAGENTA),
                ("6", "🗑️ Удалить транзакцию", Fore.RED),
                ("7", "🎯 Управление бюджетами", Fore.LIGHTYELLOW_EX),
                ("8", "💾 Сохранить данные", Fore.WHITE),
                ("9", "🚪 Выход", Fore.LIGHTWHITE_EX)
            ]
            
            for num, text, color in menu_items:
                self.print_menu_item(num, text, color)
            
            print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")
            
            choice = input(f"{Fore.YELLOW}Выберите действие (1-9): {Style.RESET_ALL}").strip()
            
            actions = {
                '1': self.add_transaction,
                '2': self.view_balance,
                '3': self.view_transactions,
                '4': self.search_transactions,
                '5': self.show_statistics,
                '6': self.delete_transaction,
                '7': self.manage_budgets,
                '8': self.save_data,
                '9': self.exit_app
            }
            
            if choice in actions:
                actions[choice]()
            else:
                self.print_error("Неверный выбор. Пожалуйста, выберите 1-9")
    
    def exit_app(self):
        """Красивый выход из приложения"""
        print(f"\n{Fore.YELLOW}💾 Сохраняем данные...{Style.RESET_ALL}")
        self.save_data()
        
        goodbye = f"""
{Fore.YELLOW}╔══════════════════════════════════════════════════════════╗
║                                                              ║
║   👋 {Fore.CYAN}Спасибо за использование программы!{Fore.YELLOW}                  ║
║                                                              ║
║   {Fore.GREEN}💰 Данные сохранены{Fore.YELLOW}                                       ║
║   {Fore.BLUE}📊 До новых встреч!{Fore.YELLOW}                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(goodbye)
        time.sleep(1)
        exit()

def main():
    """
    Точка входа в программу
    """
    try:
        app = FinancialApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Программа прервана пользователем.{Style.RESET_ALL}")
        # Пытаемся сохранить данные при прерывании
        if 'app' in locals():
            app.save_data()
    except Exception as e:
        print(f"\n{Fore.RED}❌ Произошла ошибка: {e}{Style.RESET_ALL}")
        print("Программа будет закрыта.")
        if 'app' in locals():
            app.save_data()

if __name__ == "__main__":
    main()
