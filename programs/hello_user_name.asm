section .data

question:
    word 17, "What's your name?"

new_line_ch:
    word 10

greeting:
    word 7, "Hello, "

name:
    buf 16

section .code
    push question
    dup
    push_by
printing_question:
    jz end_question
    push 1
    dec
    swap
    push 1
    add

    dup
    push_by
    print
    swap
    jmp printing_question
end_question:
    del_tos
    del_tos
    push new_line_ch
    push_by
    print
    push 0
    push name
    push 1
    add
reading:
    dup
    input
    jz end_reading
    swap
    pop_by
    push 1
    add
    swap
    push 1
    add
    dup
    push 15
    dec
    jz buf_overflow
    del_tos
    swap
    jmp reading
buf_overflow:
    del_tos
    jmp push_size
end_reading:
    del_tos
    del_tos
    swap
push_size:
    push name
    pop_by
    del_tos

    push greeting
    dup
    push_by
printing_greeting:
    jz end_greeting
    push 1
    dec
    swap
    push 1
    add

    dup
    push_by
    print
    swap
    jmp printing_greeting
end_greeting:
    del_tos
    del_tos
    push name
    dup
    push_by
printing_name:
    jz end_name
    push 1
    dec
    swap
    push 1
    add

    dup
    push_by
    print
    swap
    jmp printing_name
end_name:
    del_tos
    del_tos
    halt