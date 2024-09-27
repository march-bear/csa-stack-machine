section .data
    max_word:
        word 2147483647

section .code
    push max_word
    push_by
    push 1
    add
    print
    halt