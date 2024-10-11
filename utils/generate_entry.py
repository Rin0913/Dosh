import os

here = os.path.abspath(__file__)
here = os.path.dirname(here)
here = os.path.dirname(here)
dosh = os.path.join(here, "main.py")

print(f'''
#include <stdio.h>
#include <unistd.h>
int main() {{
    char result[50];
    uid_t real_uid = getuid();
    if(setuid(0) != 0) {{
        printf("setuid failed");
        return 1;
    }}
    snprintf(result, sizeof(result), "%s %d", "{dosh}", real_uid);
    system(result);
}}''')
