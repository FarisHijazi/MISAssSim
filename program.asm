
.data
@array  .dword 1,2,3,4

.text

@L1
add r0 = r1, r2, r1
j @useless
@useless
add R0 = R0, R0, R0 // Rd =  Ra + Rb + Rc
@repeat
add R0 = R1, R2, R3 // Rd =  Ra + Rb + Rc
add R0 = R1, R2, R3 // Rd =  Ra + Rb + Rc
add R0 = R1, R2, R3 // Rd =  Ra + Rb + Rc
add R0 = R1, R2, R3 // Rd =  Ra + Rb + Rc
j @repeat

