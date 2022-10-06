import numpy as np
import random
import data_classlib
from data_classlib import Knowledge, SimpleAssociation, Fact, FactAssociation
import dbi_classlib as dbi
#import time
import nndisplay as disp
               
from dbi_classlib import kdb, sadb, fdb, memwdb, memidb, memadb

dbi.import_necessary(items = {'Knowledge': Knowledge,
                              'SimpleAssociation': SimpleAssociation,
                              'Fact': Fact,
                              'FactAssociation': FactAssociation})

data_classlib.import_necessary(items = {'kdb': kdb,
                                        'sadb': sadb})
import bam
bam.import_necessary(items = {'Knowledge': Knowledge,
                              'SimpleAssociation': SimpleAssociation,
                              'Fact': Fact,
                              'FactAssociation': FactAssociation,
                              'kdb': kdb,
                              'sadb': sadb,
                              'fdb': fdb,
                              'memwdb': memwdb,
                              'memidb': memidb,
                              'memadb': memadb})

bam.create_empty_IA()
# Передача БД индукционных характеристик.
dbi.finish_import_necessary(items = {'I': bam.I, 'A': bam.A})

facts_to_associations = [
    ('Большая панда', ['Панда#5']),
    ('Большая панда', ['Ест бамбук#5']),
    ('Большая панда', ['Медведь#5']),
    ('Большая панда', ['Четвероногое#5']),
    ('Большая панда', ['Неопасное#5']),
    ('Большая панда', ['Занесено в Красную книгу#5']),
    ('Большая панда', ['Обитает в горах#5']),
    #('Горы', ['Обитает в горах#1']),
    ('Всеядное', ['Ест мясо#4']),
    ('Всеядное', ['Ест растительную пищу#4']),
    ('Медвежьи', ['Медведь#3']),
    ('Млекопитающие', ['Позвоночное#2']),
    ('Бурый медведь', ['Ест мёд#5']),
    ('Бурый медведь', ['Опасное#5']),
    ('Бурый медведь', ['Медведь#5']),
    ('Бурый медведь', ['Четвероногое#5']),
    ('Бурый медведь', ['Ест рыбу#5']),
    ('Бурый медведь', ['Ест падаль#5']),
    ('Бурый медведь', ['Обитает в лесах#5']),
    ('Тундра', ['Обитает в тундре#1']),
    ('Белый медведь', ['Опасное#5']),
    ('Белый медведь', ['Медведь#5']),
    ('Белый медведь', ['Четвероногое#5']),
    ('Белый медведь', ['Ест рыбу#5']),
    ('Белый медведь', ['Ест падаль#5']),
    ('Белый медведь', ['Обитает в тундре#5']),
    ('Серый волк', ['Собака#5']),
    ('Серый волк', ['Неопасное#5']),
    ('Серый волк', ['Позвоночное#5']),
    ('Серый волк', ['Четвероногое#5']),
    ('Серый волк', ['Ест мясо#5']),
    ('Серый волк', ['Обитает в степях#5']),
    ('Тайга', ['Обитает в тайге#1']),
    ('Малая панда', ['Собака#5']),
    ('Малая панда', ['Неопасное#5']),
    ('Малая панда', ['Позвоночное#5']),
    ('Малая панда', ['Ест растительную пищу#5']),
    ('Малая панда', ['Панда#5']),
    ('Малая панда', ['Ест бамбук#5']),
    ('Малая панда', ['Обитает в горах#5']),
    ('Собака домашняя', ['Собака#5']),
    ('Собака домашняя', ['Неопасное#5']),
    ('Собака домашняя', ['Домашнее#5']),
    ('Собака домашняя', ['Четвероногое#5']),
    ('Собака домашняя', ['Ест корм#5']),
    ('Собака домашняя', ['Обитает в городах#5']),
    ('Человек разумный', ['Разумное#5']),
    ('Человек разумный', ['Опасное#5']),
    ('Человек разумный', ['Прямоходящее#5']),
    ('Человек разумный', ['Примат#5']),
    ('Человек разумный', ['Ест рыбу#5']),
    ('Человек разумный', ['Обитает в городах#5']),
    ('Гоминиды', ['Примат#3']),
    ('Западная горилла', ['Неопасное#5']),
    ('Западная горилла', ['Человекообразная обезьяна#5']),
    ('Западная горилла', ['Ест растительную пищу#5']),
    ('Западная горилла', ['Обитает в лесах#5']),
    ('Филин обыкновенный', ['Сова#5']),
    ('Филин обыкновенный', ['Неопасное#5']),
    ('Филин обыкновенный', ['Яйцекладущее#5']),
    ('Филин обыкновенный', ['Обитает в степях#5']),
    ('Филин обыкновенный', ['Ест падаль#5']),
    ('Филин обыкновенный', ['Крылатое#5']),
    ('Совиные', ['Сова#3']),
    ('Совиные', ['Яйцекладущее#3']),
    ('Птицы', ['Крылатое#2']),
    ('Птицы', ['Позвоночное#2']),
    ('Белая сова', ['Сова#5']),
    ('Белая сова', ['Неопасное#5']),
    ('Белая сова', ['Обитает в тундре#5']),
    ('Белая сова', ['Крылатое#5']),
    ('Сизый голубь', ['Голубь#5']),
    ('Сизый голубь', ['Неопасное#5']),
    ('Сизый голубь', ['Переносчик инфекций#5']),
    ('Сизый голубь', ['Ест растительную пищу#5']),
    ('Голубиные', ['Голубь#3']),
    ('Голубиные', ['Переносчик инфекций#3']),
    ('Гребнистый крокодил', ['Крокодил#5']),
    ('Гребнистый крокодил', ['Опасное#5']),
    ('Гребнистый крокодил', ['Яйцекладущее#5']),
    ('Гребнистый крокодил', ['Обитает в прибрежье#5']),
    ('Гребнистый крокодил', ['Ест мясо#5']),
    ('Гребнистый крокодил', ['Позвоночное#5']),
    ('Настоящие крокодилы', ['Крокодил#3']),
    ('Настоящие крокодилы', ['Яйцекладущее#3']),
    ('Пресмыкающиеся', ['Позвоночное#2']),
    ('Прибрежье', ['Обитает в прибрежье#1'])]

# Режим запуска модуля: с нуля или при имеющихся БД ДАП.
memw_mode, memia_mode = 'l', 'l'

# Обучение нейросети на картах паттернов.
def learn_bam():

    console = bam.infer_by_deduction(recall_mode = 'out',
                                     do_induction = True,
                                     do_abduction = True)
    print(next(console))
    f_names = list(fdb)
    for i in range(50):
        random.shuffle(f_names)
        for f_name in f_names:
            console.send(f_name)
            
    console = bam.infer_by_deduction(recall_mode = 'out',
                                     do_induction = True,
                                     do_abduction = True,
                                     print_idata = True)
    print(next(console))
    for f_name in fdb:
        print(console.send(f_name))  

    #if memw_mode == 'c':
    bam.save_W()
    #if memia_mode == 'c':
    bam.save_IA()

# Тестирование базы данных.
def test_kdb():

    def append_knowledges_of_fact(k_args_list):
        new_knowledges_args = k_args_list
        new_knowledges = []
        for knowledge_args in new_knowledges_args:
            K = kdb.append(**knowledge_args)
            if K: new_knowledges.append(K.name)
            else: new_knowledges.append(knowledge_args['k_name'])
        return new_knowledges

    def append_assocs_of_factassoc(fa_args_list):
        new_assocs_args = fa_args_list
        new_assocs = []
        for assoc_args in new_assocs_args:
            SA = sadb.append(**assoc_args)
            if SA: new_assocs.append(SA.name)
            else: new_assocs.append(str(sadb.get(sadb.id_of(assoc_args['k_name'], full_match = False))))
        return new_assocs

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Большая панда', 'sign': '@' },
        { 'k_name': 'Всеядное', 'sign': '<4>' },
        { 'k_name': 'Млекопитающие', 'sign': '<2>' }])
    F1 = fdb.append('Большая панда', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Бурый медведь', 'sign': '@' },
        { 'k_name': 'Всеядное', 'sign': '<4>' },
        { 'k_name': 'Медвежьи', 'sign': '<3>' },
        { 'k_name': 'Млекопитающие', 'sign': '<2>' },
        { 'k_name': 'Горы', 'sign': 'Ω' },
        { 'k_name': 'Леса', 'sign': 'Ω' },
        { 'k_name': 'Тундра', 'sign': 'Ω' }])
    F2 = fdb.append('Бурый медведь', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Белый медведь', 'sign': '@' },
        { 'k_name': 'Хищник', 'sign': '<4>' },
        { 'k_name': 'Млекопитающие', 'sign': '<2>' }])
    F3 = fdb.append('Белый медведь', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Серый волк', 'sign': '@' },
        { 'k_name': 'Псовые', 'sign': '<3>' },
        { 'k_name': 'Леса', 'sign': 'Ω' },
        { 'k_name': 'Тайга', 'sign': 'Ω' },
        { 'k_name': 'Тундра', 'sign': 'Ω' },
        { 'k_name': 'Степи', 'sign': 'Ω' },
        { 'k_name': 'Горы', 'sign': 'Ω' }])
    F3 = fdb.append('Серый волк', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Малая панда', 'sign': '@' },
        { 'k_name': 'Травоядное', 'sign': '<4>' },
        { 'k_name': 'Пандовые', 'sign': '<3>' }])
    F4 = fdb.append('Малая панда', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Собака домашняя', 'sign': '@' },
        { 'k_name': 'Всеядное', 'sign': '<4>' },
        { 'k_name': 'Млекопитающие', 'sign': '<2>' },
        { 'k_name': 'Города', 'sign': 'Ω' }])
    F5 = fdb.append('Собака домашняя', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Человек разумный', 'sign': '@' },
        { 'k_name': 'Гоминиды', 'sign': '<3>' },
        { 'k_name': 'Млекопитающие', 'sign': '<2>' }])
    F6 = fdb.append('Человек разумный', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Западная горилла', 'sign': '<3>' },
        { 'k_name': 'Гоминиды', 'sign': '<3>' },
        { 'k_name': 'Млекопитающие', 'sign': '2' }])
    F6 = fdb.append('Западная горилла', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Филин обыкновенный', 'sign': '@' },
        { 'k_name': 'Хищник', 'sign': '<4>' },
        { 'k_name': 'Птицы', 'sign': '<2>' },
        { 'k_name': 'Степи', 'sign': 'Ω' },
        { 'k_name': 'Тайга', 'sign': 'Ω' }])
    F7 = fdb.append('Филин обыкновенный', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Белая сова', 'sign': '@' },
        { 'k_name': 'Хищник', 'sign': '<4>' },
        { 'k_name': 'Совиные', 'sign': '<3>' }])
    F8 = fdb.append('Белая сова', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Сизый голубь', 'sign': '@' },
        { 'k_name': 'Травоядное', 'sign': '<4>' },
        { 'k_name': 'Города', 'sign': 'Ω' }])
    F9 = fdb.append('Сизый голубь', Ks)

    Ks = append_knowledges_of_fact([
        { 'k_name': 'Гребнистый крокодил', 'sign': '@' }])
    F10 = fdb.append('Гребнистый крокодил', Ks)

    # Те знания, которые не вошли ни в один факт изначально.
    Ks = append_knowledges_of_fact([
        { 'k_name': 'Голубиные', 'sign': '<3>' },
        { 'k_name': 'Настоящие крокодилы', 'sign': '<3>' },
        { 'k_name': 'Пресмыкающиеся', 'sign': '<2>' },
        { 'k_name': 'Прибрежье', 'sign': 'Ω' }])

    SA1 = append_assocs_of_factassoc([
        { 'k_name': 'Панда', 'sign': '@' }])
    SA2 = append_assocs_of_factassoc([
        { 'k_name': 'Ест бамбук', 'sign': '@' }])
    SA3 = append_assocs_of_factassoc([
        { 'k_name': 'Медведь', 'sign': '@' }])
    SA4 = append_assocs_of_factassoc([
        { 'k_name': 'Неопасное', 'sign': '@' }])
    SA5 = append_assocs_of_factassoc([
        { 'k_name': 'Занесено в Красную книгу', 'sign': '@' }])
    SA6 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в горах', 'sign': '@' }])
    SA2 = append_assocs_of_factassoc([
        { 'k_name': 'Ест рыбу', 'sign': '@' }])
    SA2 = append_assocs_of_factassoc([
        { 'k_name': 'Ест мясо', 'sign': '<4>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Ест растительную пищу', 'sign': '<4>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Медведь', 'sign': '<3>' }])
    #SA8 = append_assocs_of_factassoc([
    #    { 'k_name': 'Четвероногое', 'sign': '<2>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Позвоночное', 'sign': '<2>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в горах', 'sign': 'Ω' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Ест мёд', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Опасное', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Четвероногое', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Ест падаль', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в лесах', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в лесах', 'sign': 'Ω' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в тундре', 'sign': 'Ω' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в тундре', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Собака', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Позвоночное', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Ест мясо', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в степях', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в тайге', 'sign': 'Ω' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Ест растительную пищу', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Неопасное', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Домашнее', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в городах', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Ест корм', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Разумное', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Прямоходящее', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Примат', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Примат', 'sign': '<3>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Человекообразная обезьяна', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Сова', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Яйцекладущее', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Сова', 'sign': '<3>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Яйцекладущее', 'sign': '<3>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Крылатое', 'sign': '<3>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Крылатое', 'sign': '<2>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Крылатое', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Голубь', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Переносчик инфекций', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Голубь', 'sign': '<3>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Переносчик инфекций', 'sign': '<3>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Крокодил', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в прибрежье', 'sign': '@' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Крокодил', 'sign': '<3>' }])
    SA8 = append_assocs_of_factassoc([
        { 'k_name': 'Обитает в прибрежье', 'sign': 'Ω' }])

    #print(list(sadb.keys()))
    
    return

if __name__ == '__main__':

    #F = fdb.get('Бурый медведь')
    #print(F, [k.name for k in F])

    #test_kdb()
    
    if memw_mode == 'c':    
        pattern_maps = bam.create_pattern_maps(facts_to_associations)
        bam.set_W(bam.learn(*pattern_maps))
    else: bam.retract_W()
    if memia_mode == 'l': bam.retract_IA()

    #print(bam.W[bam.W[kdb.get('Тайга').F - 1, :] > 0.01])
    #print(bam.W[bam.W[kdb.get('Леса').F - 1, :] > 0.01])
    #print(bam.W[bam.W[kdb.get('Горы').F - 1, :] > 0.01])
    #print(bam.W[bam.W[kdb.get('Тундра').F - 1, :] > 0.01])
    #print(bam.W[bam.W[kdb.get('Пресмыкающиеся').F - 1, :] > 0.01])
    #print(bam.W[bam.W[kdb.get('Млекопитающие').F - 1, :] > 0.01])
    #print(bam.W[bam.W[kdb.get('Птицы').F - 1, :] > 0.01])


    #learn_bam()
    
    #print(FactAssociation('Обитает в горах#5').get_patterns('pA'))
    #for i, w in enumerate(bam.W[:, sadb.get('Обитает в горах#5').F - 1]):
    #    if w > 0: 
    #        print(kdb.get(i + 1))
    #print([sa.F for sa in sadb.records()])
    #fdb.update('Малая панда', Fact.append_knowledge, {'appending_k_key': 'Горы'})

    #console = bam.infer_by_deduction(recall_mode = 'out', print_idata = True)
    #print(next(console))
    #print(console.send('Гребнистый крокодил'))

    #print(sadb.get('Обитает в лесах#1'))
    #print(sadb.get('Обитает в горах#1'))
    #PR = kdb.get('Леса')
    #print(bam.W[PR.F - 1, CHOO.F - 1])
    #CHOO = sadb.get('Обитает в лесах#1')
    #PR = kdb.get('Леса')
    #print(bam.W[PR.F - 1, CHOO.F - 1])
    
    pass






    
