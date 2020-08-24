a = 4
import test_gram4
# print(test_gram3.a)

from test_gram3 import static


print(static.c + 4)
print(test_gram4.test_gram3.static.d)
print(test_gram4.test_gram3.b)
