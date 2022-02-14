

def separatorMode1(num):
    if num > 99:
        # Numero de 3 digitos.
        centenas = num / 100
        decenas = (num - centenas*100) / 10
        unidades = (num - decenas*10) / 1
        
    return unidades,decenas,centenas        

def separatorMode2(num):
    c = (num / 100) % 100
    d = (num / 10) % 10
    u = (num / 1) % 1
    return c, d, u

def separatorMode3(num):
    if num > 999:
        res = num % 1000
        mil = (num - res) / 1000
        res2 = res % 100
        cen = (res - res2) / 100
        res3 = res2 % 10
        dec = (res2 - res3) / 10
        uni = res3
        
        return mil, cen, dec, uni
    
    if num > 99:
        res = num%100
        cen = (num-(res))/100
        res2 = res % 10
        dec = (res-(res2))/10
        uni = res2
        return cen, dec, uni
        
[m,c, d, u] = separatorMode3(1235)

print(m , c , d , u)

