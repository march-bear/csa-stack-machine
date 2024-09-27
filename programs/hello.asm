section .data

string:
    word 13, "Hello, World!"

section .code
    push string
    dup
    push_by
printing:
    jz end
    push 1
    dec
    swap
    push 1
    add

    dup
    push_by
    print
    swap
    jmp printing
end:
    halt