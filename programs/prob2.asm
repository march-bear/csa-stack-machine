section .data
    first:
        word 1
    second:
        word 1
    sum:
        word 0

section .code
loop:
    push second
    push_by
    dup

    push first
    push_by

    add
    dup
    push 4000000
    dec
    jg end
    dup
    mod2
    jz even
    jmp update
even:
    dup
    push sum
    push_by
    add
    pop sum
update:
    pop second
    pop first
    jmp loop
end:
    push sum
    push_by
    print
    halt
    