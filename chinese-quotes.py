# Config
file_path = 'test.md'

# Code
# TODO Multiple Layers of Quotes
left_quote = False
right_quote = False
rqi = 0
with open(file_path, 'r', encoding='utf-8') as f:
    cc = f.read()

# print(cc)

content = list(cc)

for index, i in enumerate(content):
    # print(index, i)
    if i == '“':
        if left_quote:
            content[index] = '”'
            left_quote = False
        elif right_quote:
            content[rqi] = '“'
            content[index] = '”'
            right_quote = False
            # print(index, i)
        else:
            left_quote = True
            lqi = index
    elif i == '”':
        if left_quote:
            left_quote = False  # Correct
        elif right_quote:
            content[rqi] = '“'
            right_quote = False
        else:
            right_quote = True
            rqi = index


print(''.join(content))

with open(file_path, 'w+', encoding='utf-8') as f:
    f.write(''.join(content))
