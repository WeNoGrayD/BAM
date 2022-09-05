import shelve

# Функция импортирования необходимых для работы модуля классов и параметров.
def import_necessary(items: 'Словарь необходимых для работы модуля классов и параметров'):

    # Классы необходимы для работы баз данных, поскольку
    # в области видимости базы данных должно иметься имя,
    # используемое хранящимися и сохраняющимися элементами
    # в качестве имени класса.
    global Knowledge, SimpleAssociation, Fact, FactAssociation
    Knowledge = items['Knowledge']
    SimpleAssociation = items['SimpleAssociation']
    Fact = items['Fact']
    FactAssociation = items['FactAssociation']
    
    # Статическая инициализация интерфейсов баз данных.
    KnowledgesDB.static_init()
    SimpleAssociationsDB.static_init()
    FactsDB.static_init()
    BamDB.static_init()

# Функция доимпортирования необходимых для работы модуля параметров.
def finish_import_necessary(items: 'Словарь необходимых для работы модуля параметров'):

    # Сохранение в модуле базы данных индукционных характеристик.
    global memI, memA
    memI = items['I']
    memA = items['A']

# Интерфейс для связи с базой данных.
class DBInterface:
    
    # Статический конструктор.
    def static_init(): pass

    # Конструктор экземпляра.
    def __init__(self, db):
        self.storage = db

    # Получение итератора базы данных.
    def __iter__(self):
        return iter(self.storage)

    # Получение ключа по индексу в таблице индексов, если таковая есть.
    def ids(self):
        return self.itbl.keys()

    # Получение списка ключей базы данных.
    def keys(self):
        return self.storage.keys()

    # Получение ключа записи.
    #def key_of(self, record):
    #    return next(r_key for (r_key, r_value) in self.storage.items() if r_value == record)

    # Получение всех записей в базе данных.
    def records(self):
        return self.storage.values()

    # Получение всех пар ключ-запись базы данных.
    def items(self):
        return self.storage.items()

    # Получение всех пар ключ-запись базы данных через самостоятельно определяемые
    # методы получения ключей и записей.
    def items_mod(self):
        return zip(self.keys(), self.records())

    # Получение записи по простому ключу.
    def get(self, key):
        return self.storage.get(key)

    # Получение записи по простому ключу/id.
    def getin2w(self, key):
        
        if isinstance(key, int): return DBInterface.get(self, self.itbl[str(key)])
        # Предохранение от рекурсивного вызова перегруженного стандартного метода get.
        else: return DBInterface.get(self, key)

    # Получение записи только по составному ключу.
    # Предоставляется строковый ключ, который является частью составного ключа
    # (составные ключи должны поддерживаться таблицей).
    # В таблице индексов ищется запись, у которой первая часть совпадает с предоставленным ключом.
    def getwithckey(self, ckey):
        
        complex_key = self.itbl[str(DBInterface.id_of_complex(self, ckey))]
        # Метод составления ключа должен предоставляться реализацией интерфейса.
        return DBInterface.get(self, self.create_complex_key(complex_key))

    # Получение записи по составному ключу/id.
    def getwithckeyin2w(self, key):
        
        if isinstance(key, int):
            ckey = self.create_complex_key(self.itbl[str(key)])
            return DBInterface.get(self, ckey)
        else: return DBInterface.get(self, key)

    # Получение всех составных ключей, часть которых совпадает с предоставленной частью.
    def get_all(self,
                ckey: 'Сложный ключ, по которому производится поиск'):
        
        key = self.itbl(ckey) if isinstance(ckey, int) else self.deploy_complex_key(ckey)[0]
        
        return [r_key for (r_key, r_value) in self.items() if self.deploy_complex_key(r_key)[0] == key]

    # Добавление/изменение записи по ключу.
    def set(self, key, record):
        
        self.storage[key] = record

    # Добавление/изменение записи по составному ключу.
    def setwithckey(self, key, record):
        
        # Экземпляр должен предоставить реализацию метода создания составного ключа.
        self.storage[self.create_complex_key(key)] = record
   
    # Получение индекса записи по ключу при условии, что БД поддерживает простые ключи.
    def id_of(self, key):

        return int(next(r_id for (r_id, r_key) in self.itbl.items() if r_key == key))

    # Получение индекса записи по ключу при условии, что БД поддерживает простые ключи.
    def id_of_complex(self, key, *, full_match = True):

        if full_match:
            ioc_filter = lambda r_key: self.create_complex_key(r_key) == key
        else:
            ioc_filter = lambda r_key: r_key[0] == key

        return int(next(r_id for (r_id, r_key) in self.itbl.items() if ioc_filter(r_key)))

    # Установка записи индекс-ключ в таблице индексов.
    def set_id(self, r_id, r_key):
        
        self.itbl[str(r_id)] = r_key

    # Получение итератора базы данных при условии, что БД поддерживает сложные ключи.
    #def contains(self, key):
        
    #    return key in (r_ckey[0] for r_ckey in self.itbl.values())

    # Абстрактный метод добавления записи в таблицу.
    def append(self, record): pass
    
    # Обновление записи в базе данных.
    def update(self: 'Экземпляр базы данных',
               record_key: 'Ключ, по которому поизводится поиск записи',
               func_over_record: 'Операция над записью',
               fargs: 'Аргументы для операции над записью'):
        
        record = self.get(record_key)
        func_over_record(record, **fargs)
        self.set(record_key, record)
        self.storage.sync()


# Класс для работы с базой данных знаний.
class KnowledgesDB(DBInterface):

    # Статический конструктор.
    def static_init():
        
        # Класс, который фабрикует база данных.
        KnowledgesDB.fabric_class = Knowledge

        # Краткие обозначения для первого, последнего и промежуточных уровней абстракции знания.
        KnowledgesDB.designations = {'Ω': 1, '@': Knowledge.max_abstract_lvl}
        for mid_alvl in range(2, KnowledgesDB.designations['@']):
            KnowledgesDB.designations['<' + str(mid_alvl) + '>'] = mid_alvl

    def create_designation(self, i):

        if i == 1:
            return 'Ω'
        elif i == Knowledge.max_abstract_lvl: return '@'
        else: return '<' + str(i) + '>'
        
    # Конструктор экземплряа.
    def __init__(self):
        
        kdb = shelve.open(r'D:\GraduationProj\BAM\kdb', flag = 'c')
        DBInterface.__init__(self, kdb)
        # Таблица соответствия между индексом знания и его описанием.
        # Индексы нужны для минимизации объёма, занимаемого одной записью о факте.
        self.itbl = shelve.open(r'D:\GraduationProj\BAM\kitbl', flag = 'c')

    # Получение записи по ключу.
    # Переопределяет стандартный метод на метод с возможностью получения записи по ключу/id.
    def get(self, k_key): return DBInterface.getin2w(self, k_key) 
        
    # Вставка нового знания. 
    def append(self: 'Экземпляр базы данных знаний',
               k_name: 'Описание знания', *,
               sign: 'Условное обозначения знания' = '@',
               A: 'Амплитуда колебаний' = 1,
               sPhi: 'Фаза колебаний' = 0,
               prepared_knowledge: 'Уже собранное знание - опциональный вариант' = None,
               single_key: 'Эта ДБ поддерживает простые ключи?' = True):

        if single_key and k_name in self.keys(): return None
        if not prepared_knowledge:
            new_knowledge = self.fabric_class(k_name,
                                              abstract_lvl = self.designations[sign],
                                              A = A,
                                              sPhi = sPhi)
        else: new_knowledge = prepared_knowledge
        
        # id пусть будет по номеру выбранной частоты.
        new_k_id = new_knowledge.F
        if single_key:
            self.set_id(new_k_id, k_name)
            self.set(k_name, new_knowledge)
        else: 
            if new_knowledge.name in self.keys(): return None
            ckey = self.deploy_complex_key(new_knowledge.name)
            self.set_id(new_k_id, ckey)
            self.set(new_knowledge.name, new_knowledge)

        # Запись в БД индукционных характеристик паттернов ИндХ данного паттерна.
        if type(new_knowledge) == Knowledge:
            pattern_Phi = Fact('', new_knowledge.name).get_patterns('pPhi')[1]
            new_k_sPhi0 = pattern_Phi[new_k_id - 1]
            memI[0, new_k_id - 1] = new_k_sPhi0
            
        return new_knowledge

    # Отказ от возможности использования некоторых методов, предоставляемых
    # абстрактным классом DBInterface.

    def getin2w(self, key): raise NotlmplementedError()
    def getwithckey(self, ckey): raise NotlmplementedError()
    def getwithckeyin2w(self, key): raise NotlmplementedError()
    def get_all(self, key): raise NotlmplementedError()
    def setwithckey(self, key, record): raise NotlmplementedError()
    def id_of_complex(self, key): raise NotlmplementedError()

# Класс для работы с базой данных элементарных ассоциаций.
class SimpleAssociationsDB(KnowledgesDB):

    # Статический конструктор.
    def static_init():

        # Класс, который фабрикует база данных.
        SimpleAssociationsDB.fabric_class = SimpleAssociation

        return

    # Конструктор экземплряа.
    def __init__(self: 'Экземпляр базы данных элементарных ассоциаций'):
        
        sadb = shelve.open(r'D:\GraduationProj\BAM\sadb', flag = 'c')
        DBInterface.__init__(self, sadb)
        # Таблица соответствия между индексом знания и его описанием.
        # Индексы нужны для минимизации объёма, занимаемого одной записью о факте.
        self.itbl = shelve.open(r'D:\GraduationProj\BAM\saitbl', flag = 'c')
    
    # Метод составления комплексного ключа из записи в таблице индексов.
    def create_complex_key(self, ckey):
        
        return ckey[0] + SimpleAssociation.sep + str(ckey[1])

    # Метод развёртывания комплексного ключа в запись в таблице индексов.
    def deploy_complex_key(self, ckey):

        i = -1
        while ckey[i].isdigit(): i -= 1
        return (ckey[:i - SimpleAssociation.sep_len + 1], ckey[i+1:])

    # Получение записи по ключу.
    # Переопределяет стандартный метод на метод с возможностью получения записи по id/составному ключу.
    def get(self, key): return DBInterface.getwithckeyin2w(self, key)

    # Получение всех составных ключей, часть которых совпадает с предоставленной частью.
    def get_all(self, key): return DBInterface.get_all(self, key)

    # Переопределение нахождения индекса ассоциации по её имени.
    def id_of(self, key, *, full_match = True):

        return DBInterface.id_of_complex(self, key, full_match = full_match)
        
    # Вставка нового знания. 
    def append(self: 'Экземпляр базы данных простых ассоциаций',
               k_name: 'Описание ассоциации', *,
               sign: 'Условное обозначения знания' = '@',
               A: 'Амплитуда колебаний' = 1,
               sPhi: 'Фаза колебаний' = 0,
               prepared_knowledge: 'Уже собранное знание - опциональный вариант' = None):

        new_sa = KnowledgesDB.append(self, k_name,
                                     sign = sign,
                                     A = A, sPhi = sPhi,
                                     prepared_knowledge = prepared_knowledge,
                                     single_key = False)
        if not new_sa: return None
        new_sa_id = self.id_of(new_sa.name, full_match = True)       
        pattern_Phi = FactAssociation(new_sa.name).get_patterns('pPhi')[1]
        new_sa_sPhi0 = pattern_Phi[new_sa_id  - 1]
        memA[0, new_sa_id  - 1] = new_sa_sPhi0
        
        return new_sa

    # Расширение ассоциации на уровень абстракции ниже её уровня.
    def extend_spectre(self: 'Экземпляр базы данных простых ассоциаций',
                       extd_sa_key: 'Ключ для поиска ассоциации, индекс или сложный ключ',
                       extd_abstract_lvl: 'Уровень абстракции, на который надо расширить ассоциацию'):

        if isinstance(extd_sa_key, int):
            # Поиск простой ассоциации по индексу.
            extd_sa = self.get(extd_sa_key)
            # Поиск простой ассоциации с уровнем абстракции на один ниже, чем у полученной по ключу.
            # Если таковая найдена, то новая не создаётся, возвращается найденна.
            for extr_sa_key in self.get_all(extd_sa.name):
                extr_sa = self.get(extr_sa_key)
                if extr_sa.abstract_lvl == extd_abstract_lvl:
                    return extr_sa 
        else:
            # Поиск простой ассоциации с наименьшим уровнем абстракции.
            extd_sa = min(self.get_all(sa_key), key = lambda sa: sa.F)

        extr_sa = extd_sa.extend(extd_abstract_lvl)
        if not extr_sa:
            return None
        self.append(extr_sa.name, prepared_knowledge = extr_sa)
        return extr_sa

# Класс для работы с базой данных фактов.
class FactsDB(DBInterface):
    
    # Конструктор экземпляра.
    def __init__(self: 'Экземпляр базы данных фактов'):
        
        fdb = shelve.open(r'D:\GraduationProj\BAM\fdb', flag = 'c')
        DBInterface.__init__(self, fdb)

    # Создание и вставка нового факта.
    def append(self: 'Экземпляр базы данных фактов',
               f_name: 'Описание факта',
               f_knowledges: 'Компоненты факта - знания'):

        if f_name in self: return None
        new_fact = Fact(f_name, *f_knowledges)
        self.set(f_name, new_fact)
        
        return new_fact

    # Отказ от возможности использования некоторых методов, предоставляемых
    # абстрактным классом DBInterface.

    def items_mod(self): raise NotlmplementedError()
    def getin2w(self, key): raise NotlmplementedError()
    def getwithckey(self, ckey): raise NotlmplementedError()
    def getwithckeyin2w(self, key): raise NotlmplementedError()
    def get_all(self, key): raise NotlmplementedError()
    def setwithckey(self, key, record): raise NotlmplementedError()
    def id_of_complex(self, key): raise NotlmplementedError()
    def contains(self, key): raise NotlmplementedError()

# Класс для работы с хранилищем матрицы весов нейронной сети.
class BamDB(DBInterface):

    # Конструктор экземпляра.
    def __init__(self: 'Экземпляр базы данных весов НС',
                 stored_data_type: 'Выбор хранимых данных: весов или индукционных характеристик'):

        self.stored_data_type = stored_data_type
        db_path = None
        if stored_data_type == 'W':  db_path = r'D:\GraduationProj\BAM\memwdb'
        elif stored_data_type == 'I': db_path = r'D:\GraduationProj\BAM\memidb'
        elif stored_data_type == 'A': db_path = r'D:\GraduationProj\BAM\memadb'
        else:
            self = None
            return
        bamdb = shelve.open(db_path, flag = 'c')
        DBInterface.__init__(self, bamdb)

    # Переопределённый метод получения ключа.
    def keys(self):
        
        return map(lambda key: self.deploy_complex_key(key), DBInterface.keys(self))

    # Переопределение метода получения пары ключ-запись на модифицированный.
    def items(self):

        return DBInterface.items_mod(self)

    # Метод составления комплексного ключа из кортежа индексов матрицы.
    def create_complex_key(self, ckey):
        
        return str(ckey)[1:-1].replace(' ', '')

    # Метод развёртки комплексного ключа в обычное значенеи.
    # Возвращает два индекса.
    def deploy_complex_key(self, ckey):
        
        return tuple(map(lambda sind: int(sind), ckey.split(',')))

    # Переопределение метода установки записи по ключу через комплексный ключ.
    def get(self, key): return DBInterface.getwithckey(self, key)

    # Переопределение метода установки записи по ключу через комплексный ключ.
    def set(self, key, record): return DBInterface.setwithckey(self, key, record)

    # Добавление записи.
    def append(self, inds, value):
        
        if len(inds) != 2: return None
        self.set(inds, value)
        return value

    # Отказ от возможности использования некоторых методов, предоставляемых
    # абстрактным классом DBInterface.

    def items_mod(self): raise NotlmplementedError()
    def getin2w(self, key): raise NotlmplementedError()
    def getwithckey(self, ckey): raise NotlmplementedError()
    def getwithckeyin2w(self, key): raise NotlmplementedError()
    def get_all(self, key): raise NotlmplementedError()
    def setwithckey(self, key, record): raise NotlmplementedError()
    def id_of_complex(self, key): raise NotlmplementedError()

# База данных знаний.
# Поиск производится по описанию знания.
kdb = KnowledgesDB()
# База данных элементарных ассоциаций.
# Поиск производится по описанию ассоциации.
sadb = SimpleAssociationsDB()
# База данных фактов.
# Поиск производится по описанию факта.
fdb = FactsDB()
# Хранилище матрицы весов НС, или матрицы корреляции амплитудных спектров входных и выходных паттернов.
memwdb = BamDB('W')
# Хранилище фазовых индукционных характеристик входных паттернов.
# [0]: вектор начальных фаз после первичного преобразования Фурье.
# [1]: вектор пороговых разниц между текущей и начальной фазами для запуска индуктивного вывода.
# [2]: вектор дельт, на которые повышается фаза паттерна в ходе его анализа.
# Всё вместе должно давать гибкую настройку условий для запуска процесса индукции.
memidb = BamDB('I')
# Хранилище фазовых абдукционных характеристик выходных паттернов.
# [0]: вектор начальных фаз после первичного преобразования Фурье.
# [1]: вектор пороговых разниц между текущей и начальной фазами для запуска абдуктивного вывода.
# [2]: вектор дельт, на которые повышается фаза паттерна в ходе его анализа.
# Всё вместе должно давать гибкую настройку условий для запуска процесса абдукции.
memadb = BamDB('A')
