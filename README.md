# АК 2024. Лабораторная работа №3
+ Марухленко Иван Сергеевич
+ Группа P3233
+ Вариант `lisp -> asm | stack | harv | hw | instr | binary -> struct | stream | port | pstr | prob2 | cache`
+ Выполнен упрощенный вариант `asm | stack | harv | hw | instr | struct | stream | port | pstr | prob2 | -`

## Язык программирования

``` ebnf
program ::= "section .data\n" { data_line } "section .code\n" { code_line } | { code_line }

data_line ::= label "\n" 
            | "word" integer "\n" 
            | "word" pos_integer, string "\n" 
            | "buf" pos_integer "\n"

code_line ::= label "\n" 
            | instr "\n"

label ::= label_name ":"

instr ::= op0 
        | op1 label_name 
        | op2 integer
        | op2 (label_name)

op0 ::= "dup"
    | "add"
    | "dec"
    | "swap"
    | "print"
    | "input"
    | "halt"

op1 ::= "jmp_if"
    | "jmp"
    | "pop"

op2 ::= "push"

pos_integer ::= "0" | [ <any of "1-9"> ] { <any of "0-9"> }

integer ::= [ "-" ] pos_integer

string ::= '"' { <any symbol except '"'> } '"' | "'" { <any symbol except "'"> } "'"

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }
```

Код выполняется последовательно, начиная с первой строки, если секции не указаны, иначе начиная с первой строки после `section .code`

## Организация памяти
### Память команд
+ Машинное слово - не определено
+ Реализуется списком словарей, описывающих инструкции

### Память данных
+ Машинное слово - 32 бита
+ Адресное пространство линейное, адресуется числами от 0 до n

## Система команд

### Набор инструкций
### Кодирование инструкций


## Транслятор

## Модель процессора

### DataPath
![datapath diagram|100](diagrams/datapath.png)

### ControlUnit

## Тестирование