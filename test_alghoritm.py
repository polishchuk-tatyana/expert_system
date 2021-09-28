from interface import Interface
from PyQt5.QtWidgets import QApplication
import numpy as np
import json

app = QApplication([])
object = Interface()


def get_key(type_in_kod, value):
    for k, v in type_in_kod.items():
        if v == value:
            return k

######################################################################################################
###############              ЗАПОЛНЯЕМ СПИСКИ И СЛОВАРИ ДАННЫМИ            ###########################

facts = {}
if_facts = []
conclusions = []
work_memory = []
rules = {}
rules_coef = {}
coef_sure_facts = []
coef_sure_rules = []
rule_ = {}
relative_probability_list = []
facts_connection = {}
with open('rules.json', "r", encoding='utf-8') as file:
    rules_ = json.load(file)

with open('rules.json', "r", encoding='utf-8') as file:
    rules = json.load(file)
    for fact in rules.values():
        for rule in list(fact):
            index = rule.find('(')
            rule1 = rule[0:index]
            fact[rule1] = fact.pop(rule)


#генерируем относительную вероятность правила
def relative_probability():
    for rule in rules_.values():
        for key in rule.keys():
            index1 = key.find('(')
            index2 = key.find(')')
            key = key[index1+1:index2]
            relative_probability_list.append(key)


def init_coef_for_facts():
    with open("test.txt", "r", encoding ="utf-8") as file:
        for line in file:
            data = line.split("\n")
            coef = data[0].split('(')
            index = coef[1].find(')')
            coef[1] = coef[1][0:(index)]
            '''new = coef[0].split(':')
            print(new)
            for i in if_facts:
                for j in i:
                    if new[0]'''
            coef_sure_facts.append(float(coef[1]))


def init_facts():
    with open("test.txt", "r", encoding="utf-8") as file:
        for line in file:
            data = line.split("\n")
            fact = data[0].split(':')
            index = fact[1].find('(')
            fact[1] = fact[1][0:index]
            facts[fact[0]] = fact[1]


def init_connection():
    with open("test.txt", "r", encoding="utf-8") as file:
        for line in file:
            data = line.split("\n")
            fact = data[0].split(':')
            index = fact[1].find('+')
            fact[1] = fact[1][index+1:len(fact[1])]
            facts_connection[fact[0]] = fact[1]


def init_if_facts():
    for fact in rules.values():
        for key in fact:
            if_facts.append(fact[key])


def init_conclusions():
    for fact in rules.values():
        for key in fact:
            conclusions.append(int(key))


def graph_facts():
    array_facts = np.zeros((len(rules), len(facts)))
    for k in range(len(if_facts)):
        for f in if_facts[k]:
            for j in facts:
                if int(j) == f:
                    array_facts[k,int(j)-1] = int(j)

    return array_facts


def init_work_memory():
    for f in if_facts:
        for i in f:
            if i not in work_memory:
                if i not in conclusions:
                    work_memory.append(i)


def output():
    init_facts()
    init_if_facts()
    init_conclusions()
    init_work_memory()
    relative_probability()
    init_coef_for_facts()
    init_connection()
    print("----------Связи-----------")
    print(facts_connection)
    print("----------База фактов-----------")
    print(facts)
    print("----------База правил-----------")
    print(rules)
    print("----------Множество фактов условной части-----------")
    print(if_facts)
    print("----------Заключения-----------")
    print(conclusions)
    print("----------Рабочая память-----------")
    print(work_memory)
    print("----------Коэффициенты уверенности-----------")
    print(coef_sure_facts)
    print("----------Апостериорная вероятность-----------")
    print(relative_probability_list)

######################################################################################################

conflict_list = []
######################################################################################################
###############      ПОЛУЧЕНИЕ КОЭФФИЦИЕНТОВ УВЕРЕННОСТИ            ##################################

#функция нахождения коэффициентов уверенности
def coef_sure(index):
    list = []
    for item in if_facts[index]:
        list.append(facts[str(item)])
    CF = 0 #коэффициент уверенности правила
    c_r = float(relative_probability_list[index])
    for j in range(len(coef_sure_facts)):
        if conclusions[index] - 1 == j:
            c_f = coef_sure_facts[j]
            if c_r >= c_f and c_f != 0.1:
                CF = (c_r-c_f)/(1-c_f)
            elif c_r<c_f and c_f != 0.1:
                CF = (c_r-c_f)/c_f
    return CF


list_min = []  # список коэффициентов фактов условных частей -> из них находится минимум


def coef_sure_for_and(index):
    minimum = 0.0
    list_min.clear()
    CF_n = 0 #коэффициент достоверности правила
    CF = coef_sure(index)
    if len(if_facts[index]) > 1:
        for k in if_facts[index]:
            list_min.append(coef_sure_facts[k-1])
        minimum = min(list_min)
        CF_n = CF * minimum
    else:
        for k in if_facts[index]:
            list_min.append(coef_sure_facts[k-1])
            CF_n = CF * coef_sure_facts[k-1]
    return CF_n


coef_list_for_or = {}#словарь, который хранит конечный коэффициент для связи "или"
list_max = []


def coef_sure_for_or(conflict_list):
    CF_n = {}  # словарь коэффициентов уверенности
    list_max.clear()
    maximum  = 0.0
    for i in range(len(conflict_list)):
        index = if_facts.index(conflict_list[i])
        CF_n[index] = coef_sure_for_and(index)
    for cf in CF_n.values():
        list_max.append(cf)
    maximum = max(list_max)
    cf_key = get_key(CF_n, maximum)
    coef_list_for_or[cf_key] = maximum
    return maximum #вернули коэффициент уверенности правила
######################################################################################################


def min(list_min):
    min = list_min[0]
    for i in range(len(list_min)):
        if list_min[i] < min:
            min = list_min[i]
    return min


def max(list_max):
    max = list_max[0]
    for i in range(len(list_max)):
        if list_max[i] > max:
            max = list_max[i]
    return max


list_comb = []
coef_list_for_comb = {}#словарь, который хранит конечный коэффициент для связи "comb"


def coef_sure_for_comb(conflict_list):
    list_comb.clear()
    CF_n = {}  # словарь коэффициентов уверенности
    comb = 0.0
    for i in range(len(conflict_list)):
        index = if_facts.index(conflict_list[i])
        CF_n[index] = coef_sure_for_and(index)
    for cf in CF_n.values():
        list_comb.append(cf)
    if len(list_comb) > 2:
        for k in range(len(list_comb)):
            if list_comb[k] == 1 or list_comb[k+1] == 1:
                comb = 1
            elif list_comb[k] > 0 and list_comb[k+1] > 0:
                comb = list_comb[k] + list_comb[k+1] - (list_comb[k] * list_comb[k+1])
            elif (list_comb[k] * list_comb[k+1]) <= 0 and (list_comb[k] != 1 and list_comb[k] != -1) and (list_comb[k+1] != 1 and list_comb[k+1] != -1):
                comb = list_comb[k] + list_comb[k+1]
            elif list_comb[k] < 0 and list_comb[k+1] < 0:
                comb = list_comb[k] + list_comb[k+1] + (list_comb[k] * list_comb[k+1])
            elif list_comb[k] == -1 or list_comb[k+1] == -1:
                comb == -1
            list_comb[k] = comb
            if k >= len(list_comb):
                break
    else:
        if list_comb[0] == 1 or list_comb[1] == 1:
            comb = 1
        elif list_comb[0] > 0 and list_comb[1] > 0:
            comb = list_comb[0] + list_comb[1] - (list_comb[0]*list_comb[1])
        elif (list_comb[0]*list_comb[1]) <= 0 and (list_comb[0] != 1 and list_comb[0] != -1) and (list_comb[1] != 1 and list_comb[1] != -1):
            comb = list_comb[0] + list_comb[1]
        elif list_comb[0] < 0 and list_comb[1] < 0:
            comb = list_comb[0] + list_comb[1] + (list_comb[0] * list_comb[1])
        elif list_comb[0] == -1 or list_comb[1] == -1:
            comb == -1
    for cf_key in CF_n:
        coef_list_for_comb[cf_key] = comb
    '''cf_key = get_key(CF_n, comb)
    coef_list_for_comb[cf_key] = comb
    print(coef_list_for_comb)'''
    '''print(CF_n)
    print(list_comb)
    print(comb)
    print(coef_list_for_comb)'''
    return comb# вернули коэффициент уверенности правила


coef = 0


def choose_rule(goal):
    conflict_list.clear()
    for fact in range(len(conclusions)):
        #если нашли в заключениях факты которые ввели
        if goal == conclusions[fact]:
            #добавляем в конфликтный набор условную часть найденых целей
            conflict_list.append(if_facts[fact])
    for conn in facts_connection:
        if int(conn) == goal:
            # проерка на связь или
            if facts_connection[conn] == 'or':
                coef = coef_sure_for_or(conflict_list)
                index = get_key(coef_list_for_or, coef)
                return index
            # проерка на связь комб
            elif facts_connection[conn] == 'comb':
                coef = coef_sure_for_comb(conflict_list)
                index = get_key(coef_list_for_comb, coef)
                return index
            else:
                coef = coef_sure_for_or(conflict_list)
                index = get_key(coef_list_for_or, coef)
                return index

list_rules = [] #цепочка правил ОЦР
lists = [] #список левой части
ochered = [] #очередь доказаных или имеющихся фактов по которым делаем заключение


def choose_item(ochered, i):
    for rule in range(len(if_facts[i])):
        for o in ochered:
            if o == if_facts[i][rule]:
                c = ochered.index(o)
                return c


#если все условия в правиле найдены и выполняются, то добавляем туда заключительный факт(правило)
def append_facts(goal):
    #счетчик, который добавляет единицу каждый раз, когда мы проверяем имеется ли факт правила в рабочей памяти
    count = 0
    for i in range(len(if_facts)):
        for j in range(len(if_facts[i])):
            if if_facts[i][j] in work_memory:
                count += 1
                if count == len(if_facts[i]):
                    #обнуляем счетчик, когда перходим на новую итерацию i(заново подсчитываем количество фактов правила за каждым проходом первого цикла)
                    count = 0
                    if conclusions[i] not in work_memory:
                        work_memory.append(conclusions[i])
                    #если цель найдена то выходим из функции
                    if conclusions[i] == goal:
                        return True
            if j == len(if_facts[i])-1:
                count = 0
    append_facts(goal)

flag = []
n = 1000



def init_ochered(goal):
    index = choose_rule(int(goal))
    for j in range(len(if_facts[index])):
        if_list = if_facts[index]
        for k in range(len(if_list)):
            if if_list[k] not in ochered:
                ochered.append(if_list[k])
    #print('Очередь', ochered)

#####################################################################
#АЛГОРИТМ ОБРАТНОГО ВЫВОДА
'''def backward_chaining1(goal):
    # если очередь не пуста(значит функция backward_chaining сработала один раз и поместила в очередь все факты, которые есть в рабочей памяти
    # и на основе этих фактров мы формируем рабочую память для того, чтобы проверить имеется ли в конечном итоге цель, вызывая функцию append_facts)
    if ochered:
        append_facts(goal)
    if goal in work_memory:
        object.chain2.append('Цель истинна!')
        #print('Цель истинна!')
        for conn in facts_connection:
            if int(conn) == goal:
                if facts_connection[conn] == 'or':
                    print(coef_list_for_or)
                    object.chain2.append('С коэффициентом достоверности: ' + str(coef_list_for_or[goal]))
                elif facts_connection[conn] == 'comb':
                    object.chain2.append('С коэффициентом достоверности: ' + str(coef_list_for_comb[goal]))
                else:
                    index = conclusions.index(goal)
                    object.chain2.append('С коэффициентом достоверности: ' + str(coef_list_for_or[index]))
        object.chain2.append('Цепочка правил ОЦР: ' + str([i for i in list_rules]))
        return goal
    else:
        init_ochered(goal)
        o = 0
        while o != len(ochered):
            object.chain2.append('Проверяем факт <' + facts[str(ochered[o])] + '>')
            print('Проверяем факт <' + facts[str(ochered[o])] + '>')
            if ochered[o] not in work_memory:
                index = choose_rule(ochered[o])
                i = index
                # проходим по правилам
                for i in range(index, n):
                    if goal in work_memory:
                        break
                    for left_item in if_facts[index]:
                        lists.append(facts[str(left_item)])
                    for rule in rules:
                        if str(conclusions[index]) in rules[rule]:
                            flag.append(1)
                            object.chain2.append(
                                'Правило с заключением <' + facts[str(conclusions[index])] + '> есть в БП:')
                            print('Правило с заключением <' + facts[str(conclusions[index])] + '> есть в БП:')
                            object.chain2.append(
                                'P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                            print('P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                            if index + 1 not in list_rules:
                                list_rules.append(index + 1)
                            lists.clear()
                            break
                    if len(flag) > 0:
                        break
                #правило удаляем
                ochered.remove(ochered[o])
                # вместо него помещаем условные части правила
                for k in range(len(if_facts[index])):
                    ochered.insert(o+k, if_facts[index][k])
                #print(ochered)
                # выбираем с какого элемента в очереди идти(идем с первого эл. текущего правила)
                o = choose_item(ochered, index)
            elif ochered[o] in work_memory:
                object.chain2.append('Факт есть в РП')
                print('Факт есть в РП')
                o = o + 1
            if o == len(ochered):
                backward_chaining1(goal)
'''
def backward_chaining(goal):
    # если очередь не пуста(значит функция backward_chaining сработала один раз и поместила в очередь все факты, которые есть в рабочей памяти
    # и на основе этих фактров мы формируем рабочую память для того, чтобы проверить имеется ли в конечном итоге цель, вызывая функцию append_facts)
    if ochered:
        append_facts(goal)
    if goal in work_memory:
        object.chain.append('Ціль істинна!')
        #print('Цель истинна!')
        for conn in facts_connection:
            if int(conn) == goal:
                if facts_connection[conn] == 'or':
                    print(coef_list_for_or)
                    index = conclusions.index(goal)
                    object.chain.append('З коефіцієнтом достовірності: ')
                    object.result.append(
                        'Можно з впевненістю '+ " зробити висновок, що " + facts[str(goal)] + ', якщо ')
                elif facts_connection[conn] == 'comb':
                    print(coef_list_for_or)
                    index = conclusions.index(goal)
                    object.chain.append('З коефіцієнтом достовірності: ')
                    object.result.append(
                        'Можно з впевненістю ' + " зробити висновок, що " + facts[
                            str(goal)] + ', якщо ')
                else:
                    index = conclusions.index(goal)
                    object.chain.append('З коефіцієнтом досстовірності: ')
                    object.result.append('Можно з впевненістю ' + " зробити висновок, що " + facts[str(goal)]
                                         + ', якщо ')
        # object.chain.append('Ланцюжок правил : ' + str([i for i in list_rules]))
        return True
    else:
        init_ochered(goal)
        o = 0
        while o != len(ochered):
            object.chain.append('Перевіряєм факт <' + facts[str(ochered[o])] + '>')
            print('Проверяем факт <' + facts[str(ochered[o])] + '>')
            if ochered[o] not in work_memory:
                index = choose_rule(ochered[o])
                i = index
                # проходим по правилам
                for i in range(index, n):
                    if goal in work_memory:
                        break
                    for left_item in if_facts[index]:
                        lists.append(facts[str(left_item)])
                    for rule in rules:
                        if str(conclusions[index]) in rules[rule]:
                            flag.append(1)
                            object.chain.append(
                                'Правило з наслідком <' + facts[str(conclusions[index])] + '> є в БП:')
                            print('Правило с заключением <' + facts[str(conclusions[index])] + '> есть в БП:')
                            object.chain.append(
                                'P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                            print('P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                            if index + 1 not in list_rules:
                                list_rules.append(index + 1)
                            lists.clear()
                            break
                    if len(flag) > 0:
                        break
                #правило удаляем
                ochered.remove(ochered[o])
                # вместо него помещаем условные части правила
                for k in range(len(if_facts[index])):
                    ochered.insert(o+k, if_facts[index][k])
                #print(ochered)
                # выбираем с какого элемента в очереди идти(идем с первого эл. текущего правила)
                o = choose_item(ochered, index)
            elif ochered[o] in work_memory:
                object.chain.append('Факт є в РП')
                print('Факт є в РП')
                o = o + 1
            if o == len(ochered):
                backward_chaining(goal)
    '''for con in range(len(conclusions)):
        if conclusions[con] == goal and con != index:
            go_chaining1(con)'''

    #print('Очередь', ochered)
    #print(list_rules)
    #print('Цепочка правил ОЦР', list_rules)
    #print('work_mem', work_memory)
    '''if facts_connection[str(goal)] == 'or':
        object.result.append('Система пропонує вибрати правило - ' + 'P' + str(conclusions[index]-9))
    elif facts_connection[str(goal)] == 'comb':
        object.result.append('Система пропонує застосувати обидва правила')'''



output()


def show_rules():
    str2 = []
    for i in range(len(if_facts)):
        str1 = 'P' + str(i+1)
        for j in if_facts[i]:
            str2.append(facts[str(j)])
        str3 = facts[str(conclusions[i])]
        object.rules.append(str1 + ":" + str(str2) + '-> ' + str3)
        str2.clear()
    for w in range(len(work_memory)):
        object.facts.append(facts[str(work_memory[w])])


'''def go_chaining1(index):
    if object.go_chain1.text() == 'Вывести цепочку рассуждений':
        # index = choose_rule(int(goal))
        for left_item in if_facts[index]:
            lists.append(facts[str(left_item)])
        for rule in rules:
            if str(conclusions[index]) in rules[rule]:
                object.chain2.append('Правило с заключением <' + facts[str(conclusions[index])] + '> есть в БП:')
                print('Правило с заключением <' + facts[str(conclusions[index])] + '> есть в БП:')
                object.chain2.append(
                    'P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                print('P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                if index+1 not in list_rules:
                    list_rules.append(index+1)
                lists.clear()
                break
        object.chain2.append(str(backward_chaining1(int(conclusions[index]))))
        object.go_chain1.setText('Сброс')
    elif object.go_chain1.text() == 'Сброс':
        object.chain2.clear()
        object.goal.clear()
        object.go_chain1.setText('Вывести цепочку рассуждений')
'''
def go_chaining():
    find_list = []
    goal_text = object.goal.text()
    goal = get_key(facts, goal_text)
    for fact in range(len(conclusions)):
        #если нашли в заключениях факты которые ввели
        if int(goal) == conclusions[fact]:
            #добавляем в конфликтный набор условную часть найденых целей
            find_list.append(if_facts[fact])


    if facts_connection[goal] == 'or' or facts_connection[goal] == 'comb' or facts_connection[goal] == 'and':
        str_ = "В базі правил знайдено два правила, заключна частина якого є ціль " + goal_text
        object.find.append(str_ + " зі зв'язком " + facts_connection[goal])
    else:
        object.find.append("В базі правил знайдено правило, заключна частина якого є ціль " + goal_text)
    str2 = []
    for f in range(len(find_list)):
        for i in range(len(if_facts)):
            if if_facts[i] == find_list[f]:
                str1 = 'P' + str(i + 1)
                for j in if_facts[i]:
                    str2.append(facts[str(j)])
                str3 = facts[str(conclusions[i])]
        object.find.append(str1 + ":" + str(str2) + '-> ' + str3 + "(" + str(coef_sure_facts[int(find_list[f][0])-1])+")")
        str2.clear()
    if facts_connection[goal] == 'or':
        object.find.append('Система вибере одне із правил!')
        object.find.append("Вибираємо правило з найбільшим коефіцієнтом впевненості")
    elif facts_connection[goal] == 'comb':
        object.find.append('Система скомбінує ці два правила!')
    else:
        object.find.append('Обираємо правило з найменшим коефіцієнтом впевненості')
    if object.go_chain1.text() == 'Вивести ланцюжок міркувань' and goal_text != "":
        index = choose_rule(int(goal))
        for left_item in if_facts[index]:
            lists.append(facts[str(left_item)])
        for rule in rules:
            if str(conclusions[index]) in rules[rule]:
                object.chain.append('Правило з наслідком <' + facts[str(conclusions[index])] + '> є в БП:')
                print('Правило с заключением <' + facts[str(conclusions[index])] + '> есть в БП:')
                object.chain.append(
                    'P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                print('P' + str(index + 1) + ': ' + str([i for i in lists]) + ' -> ' + facts[str(conclusions[index])])
                if index+1 not in list_rules:
                    list_rules.append(index+1)
                    #print(list_rules)
                lists.clear()
                break
        object.chain.append(backward_chaining(int(goal)))
        # object.chain.append(result)
        object.go_chain1.setText('Скинути')
    elif object.go_chain1.text() == 'Скинути':
        object.chain.clear()
        object.goal.clear()
        object.go_chain1.setText('Вивести ланцюжок міркувань')



object.button.clicked.connect(show_rules)
object.go_chain1.clicked.connect(go_chaining)
object.show()
app.exec_()