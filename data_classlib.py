import numpy as np
#from scipy import fftpack

# Функция импортирования необходимых для работы модуля баз данных.
def import_necessary(items: 'Словарь необходимых для работы модуля баз данных'):

    # Базы данных необходимы для работы классов, поскольку
    # классы знаний и простых ассоциаций сохраняют себя в одних,
    # а классы фактов и сложных ассоциаций из БД извлекают первые.
    kdb = items['kdb']
    sadb = items['sadb']

    # Статическая инициализация классов.
    Knowledge.static_init(kdb)
    SimpleAssociation.static_init(sadb)
    Fact.static_init(kdb)
    FactAssociation.static_init(sadb)

# Класс элементарного знания.
class Knowledge:

    pulse_len = 1024
    xs = []
    dF = pulse_len # Для более точного преобрвзования Фурье.
    dT = 1 / dF
    max_abstract_lvl = 5
    fs_per_abstract_lvl = 100
    pattern_len = max_abstract_lvl * fs_per_abstract_lvl
    binarization_treshold = 1e-1
    max_y_eps = 1e-2

    # Статический конструктор.
    def static_init(kdb):
        
        Knowledge.xs = [(x * Knowledge.dT) for x in range(0, Knowledge.pulse_len)]
        # Распределение частот по уровням абстракции.
        Knowledge.fs_quantiz = [i * Knowledge.fs_per_abstract_lvl
                                for i in range(1, Knowledge.max_abstract_lvl + 1)]
        # Условие получение паттерна:
        Knowledge.db = kdb

    # Конструктор экземпляра.
    def __init__(self: 'Экземпляр знания',
                 k_name: 'Описание знания',
                 abstract_lvl: 'Уровень абстракции' = max_abstract_lvl, *,
                 A: 'Амплитуда колебаний' = 1.,
                 sPhi: 'Начальная фаза' = 0.):

        self.name = k_name
        self.abstract_lvl = abstract_lvl
        self.A = A
        self.sPhi = sPhi
        
        # Выбираем свободную частоту для предоставленного уровня абстракции.
        kF = max((knowledge for knowledge in self.db.records()
                            if knowledge.abstract_lvl == abstract_lvl),
                 key = lambda knowledge: knowledge.F,
                 default = (abstract_lvl - 1) * Knowledge.fs_per_abstract_lvl)
        if isinstance(kF, Knowledge): self.F = kF.F + 1
        else: self.F = kF + 1

    # Печать информации о знании.
    def __str__(self):
        
        return self.name

    # Пульс. Возвращает функцию для расчёта значения сигнала представления знания в точке x.
    def pulse(self):
        
        _2piF = np.pi * (self.F << 1)
        return lambda x: self.A * np.sin((_2piF * x) + self.sPhi)

    # Изменение амплитуды паттерна знания.
    def set_A(self, new_A):

        self.A = new_A

    # Изменение начальной фазы паттерна знания.
    def set_sPhi(self, new_sPhi):

        self.sPhi = new_sPhi  

# Элементарная ассоциация.
class SimpleAssociation(Knowledge):

    # Разделитель для нумерации копий в их именах.
    # Копии появляются в результате расширения ассоциации на нижние уровни абстракции.
    sep = '#'
    sep_len = len(sep)

    # Статический конструктор.
    def static_init(sadb):
        
        SimpleAssociation.db = sadb

    # Конструктор экземпляра.
    def __init__(self: 'Экземпляр знания',
                 sa_name: 'Описание простой ассоциации',
                 abstract_lvl: 'Уровень абстракции' = Knowledge.max_abstract_lvl, *,
                 A: 'Амплитуда колебаний' = 1.,
                 sPhi: 'Начальная фаза' = 0.):

        Knowledge.__init__(self, sa_name, abstract_lvl, A = A, sPhi = sPhi)
        # Добавление или изменение номера копии ассоциации.
        if sa_name[-1].isdigit():
            self.name = str(self) + SimpleAssociation.sep + str(abstract_lvl)
        else: self.name += SimpleAssociation.sep + str(abstract_lvl)

    # Метод для получения "нормального" имени без лишних символов.
    def __str__(self):
        return self.name[:-(SimpleAssociation.sep_len + len(str(self.abstract_lvl)))]

    # Расширение ассоциации на более нижний уровень абстракции.
    def extend(self, extd_abstract_lvl):

        if extd_abstract_lvl >= self.abstract_lvl: return None
        
        # Расширить ассоциацию на более нижний уровень нельзя, если уровень абстракции минимален.
        if self.abstract_lvl == 1: return None
        return SimpleAssociation(self.name, extd_abstract_lvl)

# Класс факта - сборного понятия, включающего одно или более знание.
class Fact:

    # Статический конструктор.
    def static_init(kdb):
        
        Fact.db = kdb

    # Конструктор экземпляра.
    def __init__(self: 'Экземпляр факта',
                 f_name: 'Описание факта',
                 kmain_key: 'Описание главной составляющей (знания) факта',
                 *kgeneralizations_keys: 'Описания обобщающих составляющих факта'):
        
        self.name = f_name
        fact_knowledges = [kmain_key] + list(kgeneralizations_keys)
        if isinstance(kmain_key, int): self.knowledges_ids = fact_knowledges
        else: self.knowledges_ids = [self.db.id_of(k_name) for k_name in fact_knowledges]
        # Сортировка знаний по возрастанию уровня абстракции и в алфавитном порядке.
        knowledges_ids_by_ablvl = [(knowledge.abstract_lvl, str(knowledge), knowledge_id)
                                   for (knowledge_id, knowledge)
                                   in [(knowledge_id, self.db.get(knowledge_id))
                                       for knowledge_id in self.knowledges_ids]]
        knowledges_ids_by_ablvl.sort(key = lambda k: (k[0], k[1]))
        self.knowledges_ids = [k_id for (k_ablvl, k_name, k_id) in knowledges_ids_by_ablvl]
        return

    # Перегрузка операции итерации по объекту факта.
    # Возвращает все знания-составляющие факта.
    def __iter__(self):
        return (self.db.get(k_id) for k_id in self.knowledges_ids)

    # Перегрузка операции печати объекта факта.
    def __repr__(self):

        knowledges_names = ['%s' % str(knowledge)
                            for knowledge in sorted(self, key = lambda k: (k.abstract_lvl, k.name))]
        
        return self.repr(knowledges_names)

    def repr(self, knowledges_names):

        return self.name + ': ' + (', '.join(knowledges_names)) + '.'

    # Паттерны внутренней репрезентации.
    # Функция возвращает амплитудный ПВР в форме, воспринимаемой нейросетью,
    # и фазовый спектр.
    def get_patterns(self,
                     return_params: 'Паттерны, возвращаемые методом' = 'both'):
        
        ks_patterns = [knowledge.pulse() for knowledge in self]
        pulse = np.vectorize(lambda x: sum(k_pattern(x) for k_pattern in ks_patterns))
        pulse_fft = np.fft.fft(pulse(Knowledge.xs))
        # Обрезка числа отсчётов паттерна до максимального объёма
        # паттернов в памяти (номер наивысшего уровня абстракции *
        # число отсчётов частоты на уровень абстракции).
        pulse_fft = pulse_fft[1:Knowledge.pattern_len + 1]

        pattern_A, pattern_Phi = None, None
        #cabs = lambda y: return np.sqrt((y.real ** 2) + (y.imag ** 2))

        if return_params == 'both' or return_params == 'pA':
            pA = list(map(lambda y: 2 * np.abs(y) / Knowledge.pulse_len, pulse_fft))
            # У знаний и ассоциаций могут быть разные методы получения амплитудного спектра (паттерна)
            pattern_A = self.get_pattern_A(pA)
            
        if return_params == 'both' or return_params == 'pPhi':
            pattern_Phi = np.array(list(map(lambda y: np.angle(y), pulse_fft)))

        return (pattern_A, pattern_Phi)

    def get_pattern_A(self, pA):

        maxs_quantiz = Knowledge.fs_quantiz
        max_ys = [max(pA[mq - Knowledge.fs_per_abstract_lvl : mq]) for mq in maxs_quantiz]

        # Пороговая функция для преобразования паттерна к
        # виду, воспринимаемому нейросетью.
        max_ptr = 0
        def pattern_A_treshold_func(ix) -> bool:
            i, x = ix
            nonlocal max_ptr
            if i == maxs_quantiz[max_ptr]: max_ptr += 1
            return x if ((max_ys[max_ptr] - Knowledge.max_y_eps) <= x <= max_ys[max_ptr] and
                         x > Knowledge.binarization_treshold) else 0.

        pattern_A = np.array(list(map(pattern_A_treshold_func, enumerate(pA))))
        return pattern_A

    # Добавление индекса знания в список индексов знаний-составляющих факта.
    def append_knowledge(self: 'Экземпляр факта',
                         appending_k_key: 'Описание добавляемого знания'):

        # Получение индекса добавляемого знания и его уровня абстракции.
        appending_k_id = appending_k_key if isinstance(appending_k_key, int) else self.db.id_of(appending_k_key)
        appending_knowledge = self.db.get(appending_k_key)
        appending_k_abstract_lvl = appending_knowledge.abstract_lvl
        appending_k_name = str(appending_knowledge)

        # Упорядоченная вставка индекса добавляемого знания в список индексов знаний-составляющих факта.
        for i in range(len(self.knowledges_ids)):
            k_id = self.knowledges_ids[i]
            iterated_knowledge = self.db.get(k_id)
            if iterated_knowledge.abstract_lvl >= appending_k_abstract_lvl: break
        else: i += 1
        for i in range(i, len(self.knowledges_ids)):
            k_id = self.knowledges_ids[i]
            iterated_knowledge = self.db.get(k_id)
            if (iterated_knowledge.abstract_lvl < appending_k_abstract_lvl or
                appending_k_name <= str(iterated_knowledge)): break
        else: i += 1
        self.knowledges_ids.insert(i, appending_k_id)
        
        return

    # Удаление индекса знания из списка индексов знаний-составляющих факта.
    def remove_knowledge(self: 'Экземпляр факта',
                         removing_k_key: 'Описание добавляемого знания'):

        removing_k_id = removing_k_key if isinstance(removing_k_key, int) else self.db.id_of(removing_k_name)
        self.knowledges_ids.remove(removing_k_id)
        
        return

# Сборная ассоциация.
# Не содержится в базах данных - это лишь инструмент для упаковки нескольких ассоциаций и их отображения.
class FactAssociation(Fact):

    # Статический конструктор.
    def static_init(sadb):
        
        FactAssociation.db = sadb

    # Конструктор экземпляра.
    def __init__(self: 'Экземпляр сборной ассоциации',
                 samain_key: 'Описание главной составляющей (ассоциации) сборной ассоциации',
                 *sageneralizations_keys: 'Описания обобщающих составляющих сборной ассоциации',
                 full_key_match = True):

        if full_key_match: Fact.__init__(self, 'Ассоциация', samain_key, *sageneralizations_keys)
        else:
            sa_keys = [samain_key] + list(sageneralizations_keys)
            sa_ids = [self.db.id_of(sa_key, full_match = False) for sa_key in sas_keys]
            Fact.__init__(self, 'Ассоциация', *sa_ids)

    # Перегрузка операции печати объекта факта.
    def __repr__(self):

        # Получение множества имён знаний-составляющих факта без дублей.
        all_associations_names = ['%s' % str(knowledge) for knowledge in self]
        all_associations_names.sort()
        associations_names = []
        for a_name in all_associations_names:
            if not a_name in associations_names:
                associations_names.append(a_name)

        #return self.repr([knowledge.name for knowledge in self])
        return self.repr(associations_names)
    
    def get_pattern_A(self, pA):

        pattern_A = np.array(list(map(lambda x: x if x > Knowledge.binarization_treshold else 0., pA)))
        
        return pattern_A

    # Построение сборной ассоциации из простых ассоциаций
    # с одним именем, разделённых уровнями абстракции.
    def build_multiassociation(sa_key: 'Ключ простой ассоциации, по которой требуется собрать сборную:' +
                                       'индекс или сложный ключ',
                               full_match = True):
        
        if not full_match: sa_key = FactAssociation.db.id_of(sa_key, full_match = False)

        return FactAssociation(*FactAssociation.db.get_all(sa_key)) 
