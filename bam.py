import numpy as np
import nndisplay as disp

# Функция импортирования необходимых для работы модуля классов и баз данных.
def import_necessary(items: 'Словарь необходимых для работы модуля классов и баз данных'):

    # Базы данных необходимы для работы классов, поскольку
    # классы знаний и простых ассоциаций сохраняют себя в одних,
    # а классы фактов и сложных ассоциаций из БД извлекают первые.
    global Knowledge, SimpleAssociation, Fact, FactAssociation
    Knowledge = items['Knowledge']
    SimpleAssociation = items['SimpleAssociation']
    Fact = items['Fact']
    FactAssociation = items['FactAssociation']
    
    global kdb, sadb, fdb, memwdb, memidb, memadb
    kdb = items['kdb']
    sadb = items['sadb']
    fdb = items['fdb']
    memwdb = items['memwdb']
    memidb = items['memidb']
    memadb = items['memadb']
    
    global W_shape, I_shape, A_shape
    # Размеры матрицы синаптических весов W. 
    W_shape = (Knowledge.pattern_len, Knowledge.pattern_len)
    # Размеры матрицы фазовых индукционных характеристик входных паттернов. 
    I_shape = (3, Knowledge.pattern_len)
    # Размеры матрицы фазовых абдукционных характеристик выходных паттернов. 
    A_shape = (3, Knowledge.pattern_len)

# Матрица синаптических весов.
W = None
# Минимальное значение, на которое может изменяться значение внутри матрицы весов (отрицательное).
W_epsneg = None

# Матрица фазовых индукционных характеристик входных паттернов.
I = None

# Матрица фазовых абдукционных характеристик выходных паттернов.
A = None

# Создание карт входных и выходных паттернов.
def create_pattern_maps(facts_to_associations: 'Пары имён факт-ассоциация'):

    map_len = len(facts_to_associations)
    fact_assoc_pairs = [(Fact('', fact), FactAssociation(*associations))
                        for (fact, associations) in facts_to_associations]

    facts_map = np.ndarray((map_len, Knowledge.pattern_len),
                           dtype = float,
                           buffer = np.array([pmap[0].get_patterns('pA')[0] for pmap in fact_assoc_pairs]))
    assocs_map = np.ndarray((map_len, Knowledge.pattern_len),
                            dtype = float,
                            buffer = np.array([pmap[1].get_patterns('pA')[0] for pmap in fact_assoc_pairs]))

    return (facts_map, assocs_map)

# Создание пустых матриц фазовых характеристик входных и выходных паттернов.
def create_empty_IA():

    global I, A
    
    I = np.ndarray(shape = I_shape, dtype = float)
    I[0, :] = np.zeros(I.shape[1], dtype = float)
    # Запись дельт, на которые должны повышаться фазы паттернов.
    I[1, :] = np.zeros(I.shape[1])
    i1 = 0
    # Запись пороговых значений разниц между текущей и начальной фазами паттернов для
    # запуска процесса индукции. Значение может быть меньше или равно pi, не больше.
    I[1, :] = np.array([np.pi] * I.shape[1])
    k_ablvls = iter(range(1, Knowledge.max_abstract_lvl + 1))
    for i2 in Knowledge.fs_quantiz: 
        I[2, i1:i2] = I[1, i1] / (next(k_ablvls) * 3)
        i1 = i2

    A = np.ndarray(shape = A_shape, dtype = float)
    A[0, :] = np.zeros(A.shape[1], dtype = float)
    # Запись дельт, на которые должны повышаться фазы паттернов.
    A[1, :] = np.zeros(A.shape[1])
    i1 = 0
    # Запись пороговых значений разниц между текущей и начальной фазами паттернов для
    # запуска процесса индукции. Значение может быть меньше или равно pi, не больше.
    A[1, :] = np.array([np.pi] * A.shape[1])
    k_ablvls = iter(range(1, Knowledge.max_abstract_lvl + 1))
    for i2 in Knowledge.fs_quantiz: 
        A[2, i1:i2] = A[1, i1] / (next(k_ablvls) * 3)#((Knowledge.max_abstract_lvl - next(k_ablvls) + 1) * 3)
        i1 = i2

# Создание новой матрицы синаптических весов из главного модуля.
def set_W(w: 'Созданная матрица связей'):

    global W, W_epsneg
    W = w
    W_epsneg = np.finfo(W.dtype).epsneg

# Добавление к матрице синаптических связей матрицы дополнительных связей.
def add_W(w_addition: 'Матрица дополнительных связей'):

    global W
    W += w_addition

# Сохранение матрицы синаптических весов в файл.
def save_W():
    
    for i in range(W_shape[0]):
        for j in range(W_shape[1]):
            memwdb.append((i, j), W[i, j])

# Сохранение матриц фазовых характеристик входных и выходных  паттернов в соответствующие файлы.
def save_IA():
    
    for i in range(I_shape[0]):
        for j in range(I_shape[1]):
            memidb.append((i, j), I[i, j])

    for i in range(A_shape[0]):
        for j in range(A_shape[1]):
            memadb.append((i, j), A[i, j])

# Извлечение матрицы синаптических весов из файла.
def retract_W():
    
    global W, W_epsneg
    W = np.ndarray(shape = W_shape, dtype = float)
    for (key, value) in memwdb.items():
            (i, j) = key
            W[i, j] = value
    W_epsneg = np.finfo(W.dtype).epsneg

# Извлечение матрицы индукционных характеристик из файла.
def retract_IA():
    
    global I, A
    
    I = np.ndarray(shape = I_shape, dtype = float)
    for (key, value) in memidb.items():
            (i, j) = key
            I[i, j] = value
    A = np.ndarray(shape = A_shape, dtype = float)
    for (key, value) in memadb.items():
            (i, j) = key
            A[i, j] = value

# Функция обучения ДАП инициализирует матрицу синаптических весов W
# как произведение матриц карт входных и выходных паттернов.
def learn(input_patterns_map: 'Карта входных паттернов',
          output_patterns_map: 'Карта выходных паттернов'):
    return np.matmul(input_patterns_map.T, output_patterns_map, dtype = float)

# Двоичная пороговая функция активации нейрона.
# На самом деле линейная...
def binary_treshold_func(x):
    return x if x > 0 else 0.

# Функция активации "выходных" нейронов.
# Прикладывает пороговую функцию ко взвешенным входам всех клеток памяти.
def activate(input_pattern):
    return np.vectorize(binary_treshold_func, otypes = [float])(input_pattern)

# Вызов ассоциации Y для знания X и наоборот.
def recall(input_pattern: 'Паттерн, использующийся в качестве ввода',
           mode: 'Режим вызова паттернов из памяти'):
    
    return activate(np.matmul(W.T, input_pattern) if mode == 'out' else np.matmul(W, input_pattern))

# Реализация действительного логического вывода.
# Ввод и вывод результата по запросу.
def infer_by_deduction(recall_mode: 'Режим вызова из памяти паттернов',
                       *,
                       do_induction: 'Совершать ли индуктивные выводы в этом сеансе' = False,
                       do_abduction: 'Совершать ли абдуктивные выводы в этом сеансе' = False,
                       print_idata = False):

    request_name = yield "Система реализации логических выводов запущена."

    def valid_infer(idata_key):
        
        if recall_mode == 'out':
            idata = fdb.get(idata_key)
            if not idata: idata = Fact('Факт', idata_key)
        else: idata = FactAssociation(*idata_key, full_key_match = False)
        if print_idata: print(idata)
        (request_pA, request_pPhi) = idata.get_patterns(return_params = 'both' if do_induction else 'pA')
        inferition = recall(request_pA, recall_mode)
        inferition_fs = [ind + 1 for (ind, y) in enumerate(inferition) if y > 0]
        if (inferition_fs == []): return 'NO RESULT'
        if recall_mode == 'out': odata = FactAssociation(*inferition_fs)
        else: odata = Fact('Факт', *inferition_fs)

        if do_induction: plausible_infer('i', idata, odata, idata_pPhi = request_pPhi)
        if do_abduction: plausible_infer('a', odata, idata)

        return 'INFERITION: ' + str(odata)
    
    # Процесс совершения индуктивных и/или абдуктивных выводов.
    def plausible_infer(infer_mode: 'Режим совершения правдоподобных выводов: индукции или абдукции',
                        idata: 'Данные, переданные на вход ДАП',
                        odata: 'Данные, выведенные ДАП в качестве результата её работы',
                        **patterns):

        idata_db = idata.db
        phases = I if infer_mode == 'i' else A
        # patterns.get('idata_pPhi') or idata.get_patterns('pPhi')[1] ТУТ НЕ РАБОТАЕТ
        idata_pPhi = patterns.get('idata_pPhi')
        if idata_pPhi is None: idata_pPhi = idata.get_patterns('pPhi')[1]
        
        def increase_sPhi(i, idata_atom, delta):
            new_sPhi = idata_atom.sPhi + delta
            idata_db.update(idata_atom.name, Knowledge.set_sPhi, {'new_sPhi' : new_sPhi})

        ablvls = range(Knowledge.max_abstract_lvl, 0, -1)
        # Создание словаря "уровень абстракции - входной паттерн".
        idata_atoms_by_ablvls = {ablvl: [atom for atom in idata if atom.abstract_lvl == ablvl]
                                 for ablvl in ablvls}
        buf = {}
        for (ablvl, idata_atoms) in idata_atoms_by_ablvls.items():
            if idata_atoms: buf[ablvl] = idata_atoms
        idata_atoms_by_ablvls = buf
        # Создание словаря "уровень абстракции - выходной паттерн".
        odata_atoms_by_ablvls = {ablvl: [atom for atom in odata if atom.abstract_lvl == ablvl]
                                 for ablvl in ablvls}
        buf = {}
        for (ablvl, odata_atoms) in odata_atoms_by_ablvls.items():
            if odata_atoms: buf[ablvl] = odata_atoms
        odata_atoms_by_ablvls = buf
        
        for (ida_ablvl, idata_atoms) in idata_atoms_by_ablvls.items():
            for idata_atom in idata_atoms:
                # Получение индекса паттерна знания в БД индукционных характеристик
                i = idata_atom.F - 1
                # Начальный фазовый сдвиг (занесённый в БД индукционных характеристик
                # при первом появлении знания в БД знаний), нормализованный к положительному значению.
                sPhi0 = phases[0, i] + np.pi
                #print('sPhi0:', sPhi0)
                # Текущий фазовый сдвиг, нормализованный к положительному значению.
                #cPhi = idata_pPhi[i]
                #print('cPhi:', cPhi)
                cPhi = idata_pPhi[i] + np.pi
                #print('cPhiN:', cPhi)
                # Дельта, на которую изменяется фазовый сдвиг конкретно этот паттерн. 
                delta = phases[2, i]
                # Разница между текущим и фазовым сдвигом.
                dPhi = np.abs(sPhi0 - cPhi)
                #print('dPhi:', dPhi)
                # Пороговое значение разницы для совершения индуктивного вывода.
                treshold = phases[1, i]
                #print('treshold:', treshold)
                
                # Поиск в сборной ассоциации к факту простой ассоциации
                # с тем же уровнем абстракции, что и у исследуемго знания.
                #odata_atom = odata_atoms_by_ablvls.get(ida_ablvl)
                #if not odata_atom:
                #    increase_sPhi(i, idata_atom, delta)
                #    continue
                                         
                if (treshold - dPhi < delta/2):
                    # Расширение ассоциации на знание уровнем абстракции ниже.
                    #extd_idata_atom = idata_atoms_by_ablvls.get(ida_ablvl - 1)
                    # Если паттерн факта не цельный и имеет пробелы, то расширять картину мира нет смысла.
                    #if not extd_idata_atom:
                    #increase_sPhi(i, idata_atom, delta)
                    #continue

                    # Совершение индуктивного вывода.
                    if do_induction and infer_mode == 'i':
                        infer_by_induction(idata_atom, idata_atoms_by_ablvls,
                                           extending_mode = 'by_abstract_lvl')
                    # Совершение абдуктивного вывода.
                    if do_abduction and infer_mode == 'a':
                        infer_by_abduction(idata_atom, odata, odata_atoms_by_ablvls,
                                           extending_mode = 'by_abstract_lvl')

                    # Установка начальной фазы паттерна исследуемого знания в 0.
                    idata_db.update(idata_atom.name, Knowledge.set_sPhi, {'new_sPhi' : 0})
                else:
                    # Добавление к начальной фазе паттерна исследуемого знания связанной с паттерном дельты.
                    increase_sPhi(i, idata_atom, delta)
                    #print('Порог не пройден:', treshold - dPhi)

        return
    
    while request_name != '~STOP!':
        request_name = yield valid_infer(request_name)

# Реализация правдоподобного логического вывода - индукции.
def infer_by_induction(extr_knowledge: 'Паттерн знания, у которого берутся ассоциации для дополнения',
                       #extd_knowledge: 'Паттерн знания, которое дополняется ассоциациями',
                       fact_knowledges_by_ablvls: 'Словарь "знанние-уровень абстракции" факта',
                       *,
                       extending_mode: 'Режим дополнения ассоциациями' = 'all'):

    K_src = kdb.get(extr_knowledge) if isinstance(extr_knowledge, str) else extr_knowledge
    i_src = K_src.F - 1
    
    global W
    # Если режим дополнения ассоциациями простой, то все ассоации копируются из строки в строку.
    if extending_mode == 'all': W[i_dst, :] += W[i_src - 1, :]
    # Если режим - по уровням абстракции, то идёт тонкая настройка.
    elif extending_mode == 'by_abstract_lvl':
        for K_dst_ablvl in range(K_src.abstract_lvl - 1, 0, -1):
            Ks_lower_ablvl = fact_knowledges_by_ablvls.get(K_dst_ablvl)
            if not Ks_lower_ablvl: continue
            for K_dst in Ks_lower_ablvl:
                i_dst = K_dst.F - 1
                already_associated = []
                fs_treshold_dst = Knowledge.fs_quantiz[K_dst_ablvl - 1]
                for j in range(fs_treshold_dst - Knowledge.fs_per_abstract_lvl,
                               fs_treshold_dst):
                    if W[i_dst, j] > 0: already_associated.append(str(sadb.get(j + 1)))

                fs_treshold_src = Knowledge.fs_quantiz[K_src.abstract_lvl - 1]
                # Берутся ассоциации только на уровне абстракции паттерна знания, что расширяет.
                # Ассоциация будет расширяться на уровни абстракции выше нынешнего.
                for j in range(fs_treshold_src - Knowledge.fs_per_abstract_lvl,
                               fs_treshold_src):
                    # Берём связи, которые меньше либо равны 0 у знания, что расширяет,
                    # и равны нулю у знания, что расширяется.
                    if W[i_src, j] <= 0 or W[i_dst, j] != 0: continue

                    extd_sa = sadb.get(j + 1)
                    # Если знание уже ассоциируется с этой ассоциацией на этом уровне,
                    # то верифицировать связь смысла нет.
                    if str(extd_sa) in already_associated: continue
                
                    # Для того, чтобы закрыть вопрос о связи знания в составе факта и
                    # просмотренной ассоцаиции, связь устанавливается в минус,
                    # т.е. система ставится в известие, что что эта связь уже была обнаружена
                    # и привела к одному из двух исходов: либо была установлена
                    # связь знания с соответствующей по уровню абстракции ассоциацией,
                    # либо связь отвергается.
                    # Связь устанавливается в минимально возможное (по модулю) отрицательное значение,
                    # чтобы отрицательные значения связей более низких уровней
                    # не перекрывали положительные значения связей более высоких
                    # при перемножении матрицы весов и входного вектора.
                    W[i_dst, j] -= W_epsneg
                
                    # Система должна верифицировать свой логический вывод.
                    verification_request = 'Система пришла к выводу, что объект ' + K_dst.name;
                    verification_request += ' должен ассоциироваться с объектом ' + extd_sa.name + '.\n'
                    verification_request += 'Запрос: вывод верен? д/н\t'
                    inferition_verificated = input(verification_request)
                    if inferition_verificated != 'д':
                        continue
            
                    # Расширение паттерна ассоциации на уровень абстракции ниже.
                    extr_sa = sadb.extend_spectre(extd_sa.F, K_dst_ablvl)
                    p = extr_sa.F - 1
                    # Добавление ассоциации к строке паттерная расширяемого знания в матрице синаптических весов.
                    W[i_dst, p] += W[i_src, j]

    return

# Реализация правдоподобного логического вывода - абдукции.
def infer_by_abduction(extr_assoc: 'Сборная ассоциация, которая может дополнить факт',
                       extd_fact: 'Факт, который дополняется имеющимися знаниями',
                       fact_knowledges_by_ablvls: 'Словарь "знанние-уровень абстракции" факта',
                       *,
                       extending_mode: 'Режим дополнения знаниями' = 'all'):

    F_dst = fdb.get(extd_fact) if isinstance(extd_fact, str) else extd_fact
    need_verification = extending_mode == 'by_abstract_lvl'

    # Для расширения факта знаниями требуется создать сборную ассоциацию
    # из всех простых ассоциаций с одним именем (и смыслом).
    # Если на одном уровне абстракции имеется пробел в факте (отсутствие знания)
    # и присутствует простая ассоциация, то факт расширяется знанием, ассоциируемым
    # с этой простой ассоциацией.
    def extend_fact_by_multiassociation(ma):
        
        for SA_src in ma:
            # Если на уровне абстракции ассоциации факт заполнен знанием, то
            # эта ассоциация пропускается.
            if SA_src.abstract_lvl in fact_knowledges_by_ablvls.keys(): continue
            j_src = SA_src.F - 1
            
            fs_treshold_src = Knowledge.fs_quantiz[SA_src.abstract_lvl - 1]
            for i in range(fs_treshold_src - Knowledge.fs_per_abstract_lvl,
                           fs_treshold_src):
                if W[i, j_src] <= 0: continue

                # Система должна верифицировать свой логический вывод.
                # Ненадёжной (поскольку может перекрываться потребностями пользователя системой)
                # мерой противодействия повторному реагированию на связь является
                # заполненность факта знаниями.
                if need_verification:
                    verification_request = 'Система пришла к выводу, что объект ' + str(kdb.get(i + 1))
                    verification_request += ' может быть обобщением факта ' + F_dst.name
                    verification_request += ' на уровне абстракции ' + str(SA_src.abstract_lvl) + '.\n'
                    verification_request += 'Запрос: вывод верен? д/н\t'
                    inferition_verificated = input(verification_request)
                    if inferition_verificated != 'д': continue

                fact_knowledges_by_ablvls[SA_src.abstract_lvl] = [kdb.get(i+1)]
                fdb.update(F_dst.name, Fact.append_knowledge, {'appending_k_key': i+1})
                break
                
        return
    
    # Если режим - по уровням абстракции, то идёт тонкая настройка.
    if isinstance(extr_assoc, str):
        A_src = FactAssociation.build_multiassociation(extr_assoc)
        extend_fact_by_multiassociation(MSA_extr)
    else:
        A_src = FactAssociation.build_multiassociation(extr_assoc.name)
        MA_src = []
        max_abstract_lvl_in_fact = max(fact_knowledges_by_ablvls.keys())
        for SA_src in A_src:
            if SA_src.abstract_lvl < max_abstract_lvl_in_fact: MA_src.append(SA_src)
            else: break
        extend_fact_by_multiassociation(MA_src)

    return
